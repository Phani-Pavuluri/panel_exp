import matplotlib.pyplot as plt
import matplotlib.cm as cm
import seaborn as sns
import numpy as np
import pandas as pd
import mlflow
import builtins
from typing import List, Dict, Any, Tuple
from panel_exp.panel_data import PanelDataset, TimePeriod, long_df_to_paneldataset
from panel_exp.methods.tbr import TBRRidge
from sklearn.preprocessing import MinMaxScaler

def create_design_comparison_dashboard(pa_df_combined, mde_percent_df, test_lengths, n_test_grps, mde_weight=0.7, balance_weight=0.3):
    """
    Create a comprehensive comparison dashboard for all designs.
    """
    # Validate weights
    if not (0 <= mde_weight <= 1 and 0 <= balance_weight <= 1):
        raise ValueError("Weights must be between 0 and 1")
    if builtins.abs(mde_weight + balance_weight - 1.0) > 1e-10:
        raise ValueError("Weights must sum to 1")
        
    # Create score weights dictionary
    score_weights = {
        'mde': mde_weight,
        'balance': balance_weight
    }
    
    with mlflow.start_run(run_name="design_comparison_dashboard", nested=True):
        # Initialize week strings
        week_strs = [f"{int(length/7)}wk" for length in test_lengths]
        
        # Calculate number of designs
        n_designs = len(mde_percent_df) // n_test_grps
        
        # Create design summary DataFrame with correct number of rows
        design_summary = pd.DataFrame({
            'design_id': [i for i in range(n_designs) for _ in range(n_test_grps)],
            'test_group': [j for _ in range(n_designs) for j in range(n_test_grps)]
        })

        # Dictionary to store summary tables for each week
        summary_tables = {}
        
        # Add metrics for each test length
        for test_length in test_lengths:
            week_str = f"{int(test_length/7)}wk"
            
            # Validate input data
            if f'{week_str}_percent' not in mde_percent_df.columns:
                raise ValueError(f"Column '{week_str}_percent' not found in mde_percent_df")
            
            # Assign MDE values with validation
            mde_values = mde_percent_df[f'{week_str}_percent'].values
            if len(mde_values) != len(design_summary):
                raise ValueError(f"Length mismatch: mde_values ({len(mde_values)}) != design_summary ({len(design_summary)})")
            design_summary[f'mde_percent_{week_str}'] = mde_values
            
            # Calculate effect sizes at 80% power for both positive and negative effects
            effect_sizes_neg = []
            effect_sizes_pos = []
            
            for i in range(len(pa_df_combined)):
                pa_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[i]
                if not isinstance(pa_data, pd.DataFrame):
                    raise ValueError(f"Power analysis data for design {i} is not a DataFrame")
                
                # Get negative effect sizes at 80% power
                neg_mask = (pa_data['power'] >= 0.8) & (pa_data['prc_effect'] < 0)
                if neg_mask.any():
                    effect_sizes_neg.append(pa_data[neg_mask]['prc_effect'].max())
                else:
                    effect_sizes_neg.append(np.nan)
                
                # Get positive effect sizes at 80% power
                pos_mask = (pa_data['power'] >= 0.8) & (pa_data['prc_effect'] > 0)
                if pos_mask.any():
                    effect_sizes_pos.append(pa_data[pos_mask]['prc_effect'].min())
                else:
                    effect_sizes_pos.append(np.nan)
            
            design_summary[f'effect_size_at_80pct_power_neg_{week_str}'] = effect_sizes_neg
            design_summary[f'effect_size_at_80pct_power_pos_{week_str}'] = effect_sizes_pos

            # Calculate minimum absolute effect size that achieves 80% power
            design_summary[f'min_abs_effect_at_80pct_power_{week_str}'] = design_summary.apply(
                lambda row: builtins.min(
                    builtins.abs(row[f'effect_size_at_80pct_power_neg_{week_str}']),
                    builtins.abs(row[f'effect_size_at_80pct_power_pos_{week_str}'])
                ) if pd.notna(row[f'effect_size_at_80pct_power_neg_{week_str}']) and 
                   pd.notna(row[f'effect_size_at_80pct_power_pos_{week_str}'])
                else np.nan,
                axis=1
            )
        
        # Add common metrics with validation
        if 'test_prc' not in mde_percent_df.columns or 'control_prc' not in mde_percent_df.columns:
            raise ValueError("mde_percent_df must contain 'test_prc' and 'control_prc' columns")
            
        design_summary['test_group_percentage'] = mde_percent_df['test_prc'].values
        design_summary['control_group_percentage'] = mde_percent_df['control_prc'].values
        
        # Create comparisons for each test length
        for week_str in week_strs:
            # Create summary table with validation
            try:
                summary_table = create_design_summary(design_summary, week_str, mde_weight=mde_weight, balance_weight=balance_weight)
                
                # Validate summary table
                if summary_table.empty:
                    raise ValueError(f"Empty summary table created for {week_str}")
                    
                required_columns = [
                    f'mde_score_{week_str}',
                    f'balance_score_norm_{week_str}',
                    f'combined_score_{week_str}'
                ]
                missing_columns = [col for col in required_columns if col not in summary_table.columns]
                if missing_columns:
                    raise ValueError(f"Missing required columns in summary table for {week_str}: {missing_columns}")
                
                # Check for valid scores
                valid_scores = summary_table[f'combined_score_{week_str}'].notna()
                if not valid_scores.any():
                    print(f"Warning: No valid combined scores found for {week_str}. Debug info:")
                    print(f"- MDE scores valid: {summary_table[f'mde_score_{week_str}'].notna().any()}")
                    print(f"- Balance scores valid: {summary_table[f'balance_score_norm_{week_str}'].notna().any()}")
                    print(f"- Number of designs: {len(summary_table)}")
                    print(f"- MDE weight: {mde_weight}, Balance weight: {balance_weight}")
                    raise ValueError(f"No valid combined scores found for {week_str}. See debug info above.")
                
                # Store the summary table
                summary_tables[week_str] = summary_table
                
                # Update design_summary with combined scores
                design_summary = design_summary.merge(
                    summary_table[[
                        'design_id', 
                        f'mde_score_{week_str}',
                        f'mde_rank_{week_str}',
                        f'balance_score_norm_{week_str}',
                        f'balance_rank_{week_str}',
                        f'combined_score_{week_str}',
                        f'combined_rank_{week_str}',
                        f'mde_percent_{week_str}_mean',
                        f'test_group_variability_{week_str}',
                        f'overall_balance_diff_{week_str}'
                    ]], 
                    on='design_id', 
                    how='left'
                )

                # Create individual test length visualizations
                create_sensitivity_heatmap(design_summary, week_str)
                create_power_curve_comparison(design_summary, pa_df_combined, week_str, n_test_grps)
                create_radar_chart(design_summary, week_str)
                
                # Generate report for this test length
                report = generate_test_length_report(design_summary, summary_table, week_str, n_designs, n_test_grps, score_weights)
                mlflow.log_text(report, f"design_comparison_report_{week_str}.md")
                mlflow.log_table(summary_tables[week_str], f"design_summary_table_{week_str}.json")
                
            except Exception as e:
                print(f"Error processing {week_str}: {str(e)}")
                print("Debug information:")
                print(f"- Design summary shape: {design_summary.shape}")
                print(f"- Available columns: {design_summary.columns.tolist()}")
                print(f"- MDE values range: {design_summary[f'mde_percent_{week_str}'].describe()}")
                print(f"- Test group percentages range: {design_summary['test_group_percentage'].describe()}")
                raise
        
        if not summary_tables:
            raise ValueError("No valid summary tables were created for any test length")
        
        # Create test length comparison
        test_length_comparison = create_test_length_comparison(summary_tables, test_lengths)
        
        # Create overall summary report
        overall_report = generate_overall_report(test_length_comparison, score_weights)
        mlflow.log_text(overall_report, "overall_comparison_report.md")
        
        return summary_table, test_length_comparison

def create_sensitivity_heatmap(design_summary, week_str):
    """
    Create a heatmap comparing MDEs, balance, and combined scores across designs.
    
    Parameters:
    -----------
    design_summary : pandas.DataFrame
        DataFrame containing design metrics
    week_str : str
        Test length string (e.g., '8wk')
    """
    # Get number of test groups
    n_test_groups = design_summary['test_group'].nunique()
    
    # If there's only one test group, create a simplified visualization
    if n_test_groups == 1:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # MDE bar plot
        sns.barplot(data=design_summary, x='design_id', y=f'mde_percent_{week_str}', ax=ax1)
        ax1.set_title(f'MDE Comparison - {week_str}')
        ax1.set_xlabel('Design ID')
        ax1.set_ylabel('|MDE| (%)')
        
        # Balance bar plot
        sns.barplot(data=design_summary, x='design_id', y='test_group_percentage', ax=ax2)
        ax2.set_title(f'Balance Comparison - {week_str}')
        ax2.set_xlabel('Design ID')
        ax2.set_ylabel('Test Group %')
        
        plt.tight_layout()
        mlflow.log_figure(fig, f"sensitivity_plot_{week_str}.png")
        plt.close()
        return
    
    # Create figure with four subplots for multiple test groups
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(20, 16))
    
    # MDE heatmap (using absolute values)
    heatmap_data_mde = design_summary.pivot_table(
        values=f'mde_percent_{week_str}',
        index='design_id',
        columns='test_group'
    )
    
    sns.heatmap(heatmap_data_mde, 
                annot=True, 
                fmt='.2f',
                cmap='YlOrRd',
                cbar_kws={'label': '|MDE| (%)'},
                ax=ax1)
    ax1.set_title(f'MDE Comparison - {week_str}')
    
    # Balance heatmap
    heatmap_data_balance = design_summary.pivot_table(
        values='test_group_percentage',
        index='design_id',
        columns='test_group'
    )
    
    sns.heatmap(heatmap_data_balance, 
                annot=True, 
                fmt='.2f',
                cmap='YlOrRd',
                cbar_kws={'label': 'Test Group %'},
                ax=ax2)
    ax2.set_title(f'Balance Comparison - {week_str}')
    
    # Combined score heatmap
    heatmap_data_combined = design_summary.pivot_table(
        values=f'combined_score_{week_str}',
        index='design_id',
        columns='test_group'
    )
    
    if not heatmap_data_combined.empty:
        sns.heatmap(heatmap_data_combined, 
                    annot=True, 
                    fmt='.2f',
                    cmap='YlOrRd',
                    cbar_kws={'label': 'Combined Score'},
                    ax=ax3)
        ax3.set_title(f'Combined Score Comparison - {week_str}')
    
    # Rankings heatmap
    rankings = pd.DataFrame({
        'MDE Rank': design_summary.groupby('design_id')[f'mde_rank_{week_str}'].first(),
        'Balance Rank': design_summary.groupby('design_id')[f'balance_rank_{week_str}'].first(),
        'Combined Rank': design_summary.groupby('design_id')[f'combined_rank_{week_str}'].first()
    })
    
    if not rankings.empty:
        sns.heatmap(rankings, 
                    annot=True, 
                    fmt='.0f',
                    cmap='YlOrRd_r',  # Reversed colormap so lower numbers are better
                    cbar_kws={'label': 'Rank (lower is better)'},
                    ax=ax4)
        ax4.set_title(f'Design Rankings - {week_str}')
    
    plt.tight_layout()
    
    # Log the figure
    mlflow.log_figure(fig, f"sensitivity_heatmap_{week_str}.png")
    plt.close()

def create_power_curve_comparison(design_summary: pd.DataFrame,
                                pa_df_combined: pd.DataFrame,
                                week_str: str,
                                n_test_groups: int) -> None:
    """
    Create both individual and comparison power curve visualizations for all designs.
    
    Parameters:
    -----------
    design_summary : pandas.DataFrame
        DataFrame containing design metrics
    pa_df_combined : pd.DataFrame
        DataFrame containing power analysis results, where each row contains a DataFrame in the pa_obj2 column
    week_str : str
        Test length string (e.g., '8wk')
    n_test_groups : int
        Number of test groups per design
    """
    # Input validation
    if design_summary.empty or pa_df_combined.empty:
        raise ValueError("Input DataFrames cannot be empty")
    
    if f'{week_str}_pa_obj2' not in pa_df_combined.columns:
        raise ValueError(f"pa_df_combined must contain column '{week_str}_pa_obj2'")
    
    # Number of total curves (one per row in pa_df_combined)
    n_total_curves = len(pa_df_combined)
    
    # Generate distinct colors
    cmap = cm.get_cmap('tab20', n_total_curves)
    colors = [cmap(i) for i in range(n_total_curves)]
    
    # Calculate number of designs
    n_designs = len(design_summary) // n_test_groups
    
    # Handle single test group case
    if n_test_groups == 1:
        # Create individual subplots for each design
        fig_individual, axes = plt.subplots(1, n_designs, figsize=(6*n_designs, 5))
        
        # Handle case where there's only one design
        if n_designs == 1:
            axes = [axes]
        
        # Plot individual power curves in separate subplots
        for design_idx in range(n_designs):
            # Get power data for this design
            power_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[design_idx]
            ax = axes[design_idx]
            
            # Validate power data structure
            if not isinstance(power_data, pd.DataFrame):
                raise ValueError(f"Power data for design {design_idx} is not a DataFrame")
            if 'prc_effect' not in power_data.columns or 'power' not in power_data.columns:
                raise ValueError(f"Power data for design {design_idx} missing required columns")
            
            # Plot power curve for this specific design
            ax.plot(power_data['prc_effect'], 
                   power_data['power'],
                   color=colors[design_idx % len(colors)],
                   linewidth=2)
            
            # Add reference lines
            ax.axhline(y=0.8, color='r', linestyle='--', alpha=0.7)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.7)
            
            # Find and annotate minimum effect size for 80% power
            power_mask = power_data['power'] >= 0.8
            if power_mask.any():
                best_power_effect = power_data[power_mask]['prc_effect'].apply(builtins.abs).min()
                ax.annotate(f'Min: {best_power_effect:.3f}%',
                           xy=(best_power_effect, 0.8),
                           xytext=(best_power_effect + 0.1, 0.9),
                           bbox=dict(facecolor='white', 
                                   edgecolor=colors[design_idx % len(colors)],
                                   alpha=0.8,
                                   boxstyle='round,pad=0.3'),
                           arrowprops=dict(facecolor=colors[design_idx % len(colors)],
                                         shrink=0.05,
                                         width=1,
                                         headwidth=6),
                           fontsize=8)
            else:
                print(f"Warning: Design {design_idx} does not achieve 80% power for any effect size")
            
            ax.set_xlabel('Effect Size (%)', fontsize=10)
            ax.set_ylabel('Power', fontsize=10)
            ax.set_title(f'Design {design_idx}', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1)
        
        # Add overall title
        plt.suptitle(f'Individual Power Curves - {week_str}', fontsize=16, y=1.02)
        plt.tight_layout()
        
        # Log individual plot to MLflow
        mlflow.log_figure(fig_individual, f"power_curves_individual_{week_str}.png")
        plt.close(fig_individual)
        
        # Create comparison plot (all curves on one plot)
        fig_comparison = plt.figure(figsize=(12, 6))
        ax_comparison = fig_comparison.add_subplot(111)
        
        # Plot all power curves on the same axes for comparison
        for design_idx in range(n_designs):
            power_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[design_idx]
            ax_comparison.plot(power_data['prc_effect'], 
                             power_data['power'],
                             label=f'Design {design_idx}',
                             color=colors[design_idx % len(colors)],
                             linewidth=2)
            
            # Find and annotate minimum effect size for 80% power
            power_mask = power_data['power'] >= 0.8
            if power_mask.any():
                best_power_effect = power_data[power_mask]['prc_effect'].apply(builtins.abs).min()
                ax_comparison.annotate(f'Design {design_idx}: {best_power_effect:.3f}',
                                     xy=(best_power_effect, 0.8),
                                     xytext=(best_power_effect + 0.1, 0.9 - (0.1 * design_idx)),
                                     bbox=dict(facecolor='white', 
                                             edgecolor=colors[design_idx % len(colors)],
                                             alpha=0.8,
                                             boxstyle='round,pad=0.5'),
                                     arrowprops=dict(facecolor=colors[design_idx % len(colors)],
                                                   shrink=0.05,
                                                   width=1.5,
                                                   headwidth=8))
        
        # Add reference lines
        ax_comparison.axhline(y=0.8, color='r', linestyle='--', label='80% Power')
        ax_comparison.axvline(x=0, color='k', linestyle='-', label='Zero Effect')
        
        ax_comparison.set_xlabel('Effect Size (%)', fontsize=12)
        ax_comparison.set_ylabel('Power', fontsize=12)
        ax_comparison.set_title(f'Power Curves Comparison - {week_str}', fontsize=14)
        ax_comparison.grid(True, alpha=0.3)
        ax_comparison.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
        plt.tight_layout()
        
        # Log comparison plot to MLflow
        mlflow.log_figure(fig_comparison, f"power_curves_comparison_{week_str}.png")
        plt.close(fig_comparison)
        return
    
    # For multiple test groups, create individual plots in a master grid
    # Create subplot grid where each subplot shows one individual power curve
    fig_individual, axes = plt.subplots(n_designs, n_test_groups, 
                                      figsize=(6*n_test_groups, 5*n_designs))
    
    # Handle case where there's only one design (axes will be 1D)
    if n_designs == 1:
        axes = axes.reshape(1, -1)
    
    # Handle case where there's only one test group (axes will be 1D)
    if n_test_groups == 1:
        axes = axes.reshape(-1, 1)
    
    # Plot individual curves in master grid
    for design_idx in range(n_designs):
        for test_group in range(n_test_groups):
            idx = design_idx * n_test_groups + test_group
            if idx >= len(pa_df_combined):
                print(f"Warning: Skipping design {design_idx}, test group {test_group} - index out of range")
                continue
                
            power_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[idx]
            ax = axes[design_idx, test_group]
            
            # Validate power data structure
            if not isinstance(power_data, pd.DataFrame):
                raise ValueError(f"Power data for design {design_idx}, test group {test_group} is not a DataFrame")
            if 'prc_effect' not in power_data.columns or 'power' not in power_data.columns:
                raise ValueError(f"Power data for design {design_idx}, test group {test_group} missing required columns")
            
            # Plot only this specific power curve (no label needed since it's individual)
            ax.plot(power_data['prc_effect'], 
                   power_data['power'],
                   color=colors[idx % len(colors)],
                   linewidth=2)
            
            # Add reference lines
            ax.axhline(y=0.8, color='r', linestyle='--', alpha=0.7)
            ax.axvline(x=0, color='k', linestyle='-', alpha=0.7)
            
            # Find and annotate minimum effect size for 80% power
            power_mask = power_data['power'] >= 0.8
            if power_mask.any():
                best_power_effect = power_data[power_mask]['prc_effect'].apply(builtins.abs).min()
                ax.annotate(f'Min: {best_power_effect:.3f}%',
                           xy=(best_power_effect, 0.8),
                           xytext=(best_power_effect + 0.1, 0.9),
                           bbox=dict(facecolor='white', 
                                   edgecolor=colors[idx % len(colors)],
                                   alpha=0.8,
                                   boxstyle='round,pad=0.3'),
                           arrowprops=dict(facecolor=colors[idx % len(colors)],
                                         shrink=0.05,
                                         width=1,
                                         headwidth=6),
                           fontsize=8)
            else:
                print(f"Warning: Design {design_idx}, test group {test_group} does not achieve 80% power for any effect size")
            
            ax.set_xlabel('Effect Size (%)', fontsize=10)
            ax.set_ylabel('Power', fontsize=10)
            ax.set_title(f'Design {design_idx} - TG {test_group}', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.set_ylim(0, 1)
    
    # Add overall title
    plt.suptitle(f'Individual Power Curves - {week_str}', fontsize=16, y=1.02)
    plt.tight_layout()
    
    # Log individual plots grid to MLflow
    mlflow.log_figure(fig_individual, f"power_curves_individual_{week_str}.png")
    plt.close(fig_individual)
    
    # Create comparison plot (all curves on one plot)
    fig_comparison = plt.figure(figsize=(12, 6))
    
    # Plot all power curves
    for design_idx in range(n_designs):
        for test_group in range(n_test_groups):
            idx = design_idx * n_test_groups + test_group
            if idx >= len(pa_df_combined):
                continue
                
            power_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[idx]
            
            # Validate power data structure
            if not isinstance(power_data, pd.DataFrame):
                raise ValueError(f"Power data for design {design_idx}, test group {test_group} is not a DataFrame")
            if 'prc_effect' not in power_data.columns or 'power' not in power_data.columns:
                raise ValueError(f"Power data for design {design_idx}, test group {test_group} missing required columns")
            
            plt.plot(power_data['prc_effect'], 
                    power_data['power'], 
                    label=f'Design {design_idx} - TG {test_group}',
                    color=colors[idx % len(colors)])
    
    # Add reference lines
    plt.axhline(y=0.8, color='r', linestyle='--', label='80% Power')
    plt.axvline(x=0, color='k', linestyle='-', label='Zero Effect')
    
    # Add annotations for each design and test group
    for design_idx in range(n_designs):
        for test_group in range(n_test_groups):
            idx = design_idx * n_test_groups + test_group
            if idx >= len(pa_df_combined):
                continue
                
            power_data = pa_df_combined[f'{week_str}_pa_obj2'].iloc[idx]
            power_mask = power_data['power'] >= 0.8
            
            if power_mask.any():
                best_power_effect = power_data[power_mask]['prc_effect'].apply(builtins.abs).min()
                
                # Calculate annotation position
                x_pos = best_power_effect + 0.1
                y_pos = 0.9 - (0.1 * idx)
                
                # Add annotation with background
                plt.annotate(f'Design {design_idx} - TG {test_group}\nEffect Size: {best_power_effect:.3f}%',
                            xy=(best_power_effect, 0.8),
                            xytext=(x_pos, y_pos),
                            bbox=dict(facecolor='white', 
                                    edgecolor=colors[idx % len(colors)],
                                    alpha=0.8,
                                    boxstyle='round,pad=0.5'),
                            arrowprops=dict(facecolor=colors[idx % len(colors)],
                                          shrink=0.05,
                                          width=1.5,
                                          headwidth=8))
    
    plt.xlabel('Effect Size (%)', fontsize=12)
    plt.ylabel('Power', fontsize=12)
    plt.title(f'Power Curves Comparison - {week_str}', fontsize=14, pad=20)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=10)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Log comparison plot to MLflow
    mlflow.log_figure(fig_comparison, f"power_curves_comparison_{week_str}.png")
    plt.close(fig_comparison)

def create_design_summary(design_summary, week_str, mde_weight=0.7, balance_weight=0.3):
    """
    Create a summary table for each design, focusing on MDE and Balance metrics.
    For designs with fixed test groups (e.g., whitelisted), balance is calculated based on control group characteristics.
    
    Parameters:
    -----------
    design_summary : pandas.DataFrame
        DataFrame containing design metrics
    week_str : str
        Test length string (e.g., '8wk')
    mde_weight : float, optional (default=0.7)
        Weight for MDE score in combined score calculation
    balance_weight : float, optional (default=0.3)
        Weight for balance score in combined score calculation
        
    Returns:
    --------
    pandas.DataFrame
        Summary table with design metrics and scores
    """
    # Validate weights
    if not (0 <= mde_weight <= 1 and 0 <= balance_weight <= 1):
        raise ValueError("Weights must be between 0 and 1")
    if builtins.abs(mde_weight + balance_weight - 1.0) > 1e-10:
        raise ValueError("Weights must sum to 1")
        
    # Create score weights dictionary
    score_weights = {
        'mde': mde_weight,
        'balance': balance_weight
    }
    
    # Initialize scaler
    scaler = MinMaxScaler(feature_range=(0, 1))
    
    # Group by design_id and calculate statistics
    summary = design_summary.groupby('design_id').agg({
        f'mde_percent_{week_str}': ['mean', 'std', 'min', 'max'],
        'test_group_percentage': ['mean', 'std'],
        'control_group_percentage': ['mean', 'std']
    }).reset_index()

    # Flatten column names
    summary.columns = ['_'.join(col).strip('_') for col in summary.columns.values]

    # Check if test group is fixed (all test percentages are identical)
    test_group_fixed = summary['test_group_percentage_std'].max() < 1e-10

    if test_group_fixed:
        # For fixed test groups, calculate balance based on control group characteristics
        test_group_target = summary['test_group_percentage_mean'].iloc[0]  # All designs have same test percentage
        
        # Calculate how well control group matches test group target
        # Use relative deviation instead of absolute to normalize the scale
        summary[f'control_group_deviation_{week_str}'] = builtins.abs(
            (summary['control_group_percentage_mean'] - test_group_target) / test_group_target
        )
        
        # Calculate control group variability (lower is better)
        # Normalize by the mean to get a relative measure of variability
        summary[f'control_group_variability_{week_str}'] = (
            summary['control_group_percentage_std'] / summary['control_group_percentage_mean']
        ).fillna(0)  # Handle case where mean is 0
        
        # Calculate balance score (lower is better)
        # Weight the components to ensure they're on similar scales
        summary[f'balance_score_{week_str}'] = (
            0.7 * summary[f'control_group_deviation_{week_str}'] +  # How well control matches test target
            0.3 * summary[f'control_group_variability_{week_str}']  # Control group stability
        )
        
        # Store the test group target for reference
        summary[f'test_group_target_{week_str}'] = test_group_target
        
        # Note that test group is fixed
        print(f"Note: Test group is fixed at {test_group_target:.1f}% across all designs. Balance score is based on control group characteristics.")
        print(f"Control group percentages: {summary['control_group_percentage_mean'].to_dict()}")
        print(f"Balance scores: {summary[f'balance_score_{week_str}'].to_dict()}")
    else:
        # Original balance calculation for variable test groups
        # Use relative differences for better scaling
        summary[f'overall_balance_diff_{week_str}'] = builtins.abs(
            (summary['test_group_percentage_mean'] - summary['control_group_percentage_mean']) / 
            summary['test_group_percentage_mean']
        )
        
        # Calculate relative variability
        summary[f'test_group_variability_{week_str}'] = (
            summary['test_group_percentage_std'] / summary['test_group_percentage_mean']
        ).fillna(0)
        
        # Calculate balance score (lower is better)
        summary[f'balance_score_{week_str}'] = (
            0.7 * summary[f'overall_balance_diff_{week_str}'] +  # Overall balance
            0.3 * summary[f'test_group_variability_{week_str}']  # Test group variability
        )

    # Normalize balance score using MinMaxScaler (higher is better)
    # Reshape for sklearn (needs 2D array)
    balance_scores = summary[f'balance_score_{week_str}'].values.reshape(-1, 1)
    # Invert the scores since lower balance score is better
    balance_scores_normalized = 1 - scaler.fit_transform(balance_scores)
    summary[f'balance_score_norm_{week_str}'] = balance_scores_normalized.flatten()

    # Calculate MDE score using MinMaxScaler (lower is better)
    # Reshape for sklearn (needs 2D array)
    mde_scores = builtins.abs(summary[f'mde_percent_{week_str}_mean'].values.reshape(-1, 1))
    # Invert the scores since lower MDE is better
    mde_scores_normalized = 1 - scaler.fit_transform(mde_scores)
    summary[f'mde_score_{week_str}'] = mde_scores_normalized.flatten()

    # Calculate combined score using the provided weights
    summary[f'combined_score_{week_str}'] = (
        score_weights['mde'] * summary[f'mde_score_{week_str}'] +
        score_weights['balance'] * summary[f'balance_score_norm_{week_str}']
    )

    # Calculate ranks (1 is best)
    summary[f'mde_rank_{week_str}'] = summary[f'mde_score_{week_str}'].rank(ascending=False, method='min')
    summary[f'balance_rank_{week_str}'] = summary[f'balance_score_norm_{week_str}'].rank(ascending=False, method='min')
    summary[f'combined_rank_{week_str}'] = summary[f'combined_score_{week_str}'].rank(ascending=False, method='min')

    # Sort by combined score
    summary = summary.sort_values(f'combined_score_{week_str}', ascending=False)

    return summary

def create_radar_chart(design_summary, week_str):
    """
    Create a radar chart comparing multiple metrics across designs.
    
    Parameters:
    -----------
    design_summary : pandas.DataFrame
        DataFrame containing design metrics
    week_str : str
        Test length string (e.g., '8wk')
    """
    # Get number of test groups
    n_test_groups = design_summary['test_group'].nunique()
    
    # If there's only one test group, create a simplified bar chart comparison
    if n_test_groups == 1:
        # Select metrics for comparison
        metrics = [
            f'mde_score_{week_str}',
            f'balance_score_norm_{week_str}',
            f'combined_score_{week_str}',
            f'mde_percent_{week_str}_mean',
            f'test_group_variability_{week_str}',
            f'overall_balance_diff_{week_str}'
        ]
        
        # Create bar chart
        fig, ax = plt.subplots(figsize=(12, 6))
        x = np.arange(len(metrics))
        width = 0.8
        
        # Plot bars for each design
        for design_id in design_summary['design_id'].unique():
            design_data = design_summary[design_summary['design_id'] == design_id]
            values = [design_data[metric].iloc[0] for metric in metrics]
            ax.bar(x + (design_id * width/len(design_summary['design_id'].unique())), 
                  values, 
                  width/len(design_summary['design_id'].unique()),
                  label=f'Design {design_id}')
        
        ax.set_ylabel('Score/Value')
        ax.set_title(f'Design Metrics Comparison - {week_str}')
        ax.set_xticks(x + width/2)
        ax.set_xticklabels(metrics, rotation=45, ha='right')
        ax.legend()
        plt.tight_layout()
        
        mlflow.log_figure(fig, f"metrics_comparison_{week_str}.png")
        plt.close()
        return
    
    # For multiple test groups, create radar chart
    # Select metrics for radar chart
    metrics = [
        f'mde_score_{week_str}',
        f'balance_score_norm_{week_str}',
        f'combined_score_{week_str}',
        f'mde_percent_{week_str}_mean',
        f'test_group_variability_{week_str}',
        f'overall_balance_diff_{week_str}'
    ]
    
    # Normalize metrics for radar chart
    normalized_data = design_summary[metrics].copy()
    for metric in metrics:
        if metric not in ['mde_score_{week_str}', 'balance_score_norm_{week_str}', f'combined_score_{week_str}']:
            normalized_data[metric] = (normalized_data[metric] - normalized_data[metric].min()) / \
                                    (normalized_data[metric].max() - normalized_data[metric].min())
    
    # Create radar chart
    fig = plt.figure(figsize=(12, 12))
    ax = fig.add_subplot(111, polar=True)
    
    # Plot each design
    for idx, row in normalized_data.iterrows():
        values = row.values
        values = np.concatenate((values, [values[0]]))  # Close the polygon
        angles = np.linspace(0, 2*np.pi, len(metrics), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Close the polygon
        ax.plot(angles, values, label=f'Design {design_summary.iloc[idx]["design_id"]}')
        ax.fill(angles, values, alpha=0.1)
    
    # Set labels
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(metrics)
    plt.title(f'Design Comparison Radar Chart - {week_str}')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    
    mlflow.log_figure(fig, f"radar_chart_{week_str}.png")
    plt.close()

def create_test_length_comparison(summary_tables, test_lengths):
    """
    Create a comparison of designs across different test lengths.
    
    Parameters:
    -----------
    summary_tables : dict
        Dictionary of summary tables for each test length
    test_lengths : list
        List of test lengths in days
        
    Returns:
    --------
    pandas.DataFrame
        Comparison table with metrics across test lengths
    """
    week_strs = [f"{int(length/7)}wk" for length in test_lengths]
    
    # Convert single DataFrame to dictionary if needed
    if not isinstance(summary_tables, dict):
        summary_tables = {week_strs[0]: summary_tables}
    
    # Handle single test length case
    if len(week_strs) == 1:
        week_str = week_strs[0]
        
        # Get the summary table for this week
        summary_table = summary_tables[week_str]
        
        # Validate that we have valid scores
        if summary_table.empty:
            raise ValueError(f"No data available for test length {week_str}")
            
        # Get the combined score column
        combined_score_col = f'combined_score_{week_str}'
        if combined_score_col not in summary_table.columns:
            raise ValueError(f"Column {combined_score_col} not found in summary table")
            
        # Check if we have any valid scores
        valid_scores = summary_table[combined_score_col].notna()
        if not valid_scores.any():
            raise ValueError(f"No valid combined scores found for test length {week_str}")
            
        # Get the best design index, handling potential nan values
        best_score_idx = summary_table.loc[valid_scores, combined_score_col].idxmax()
        if pd.isna(best_score_idx):
            raise ValueError(f"Could not determine best design for test length {week_str}")
            
        # Get all designs with the best score (handling ties)
        best_score = summary_table.loc[best_score_idx, combined_score_col]
        best_designs = summary_table[summary_table[combined_score_col] == best_score]['design_id'].tolist()
        
        comparison = pd.DataFrame({
            'test_length': [week_str],
            'best_mde_score': [summary_table[f'mde_score_{week_str}'].max()],
            'avg_mde_score': [summary_table[f'mde_score_{week_str}'].mean()],
            'best_balance_score': [summary_table[f'balance_score_norm_{week_str}'].max()],
            'avg_balance_score': [summary_table[f'balance_score_norm_{week_str}'].mean()],
            'best_combined_score': [best_score],
            'avg_combined_score': [summary_table[combined_score_col].mean()],
            'best_design': [best_designs[0] if best_designs else None],
            'best_designs': [best_designs]
        })
        
        # Create simplified visualization for single test length
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot scores
        scores = ['best_mde_score', 'avg_mde_score', 'best_balance_score', 
                 'avg_balance_score', 'best_combined_score', 'avg_combined_score']
        values = [comparison[score].iloc[0] for score in scores]
        labels = ['Best MDE', 'Avg MDE', 'Best Balance', 'Avg Balance', 
                 'Best Combined', 'Avg Combined']
        
        ax1.bar(labels, values)
        ax1.set_title('Score Comparison')
        ax1.set_xticklabels(labels, rotation=45, ha='right')
        ax1.set_ylabel('Score')
        
        # Plot design distribution
        if best_designs:
            design_counts = pd.Series(best_designs).value_counts()
            ax2.bar(design_counts.index.astype(str), design_counts.values)
            ax2.set_title('Best Design Distribution')
            ax2.set_xlabel('Design ID')
            ax2.set_ylabel('Count')
        
        plt.tight_layout()
        mlflow.log_figure(fig, "test_length_comparison.png")
        mlflow.log_table(comparison, "test_length_comparison.json")
        plt.close()
        
        return comparison
    
    # For multiple test lengths, proceed with original logic but add validation
    comparison_data = []
    
    for week_str in week_strs:
        summary_table = summary_tables[week_str]
        
        # Validate data
        if summary_table.empty:
            print(f"Warning: No data available for test length {week_str}, skipping...")
            continue
            
        combined_score_col = f'combined_score_{week_str}'
        if combined_score_col not in summary_table.columns:
            print(f"Warning: Column {combined_score_col} not found for {week_str}, skipping...")
            continue
            
        # Check for valid scores
        valid_scores = summary_table[combined_score_col].notna()
        if not valid_scores.any():
            print(f"Warning: No valid combined scores found for {week_str}, skipping...")
            continue
            
        # Get best design index
        best_score_idx = summary_table.loc[valid_scores, combined_score_col].idxmax()
        if pd.isna(best_score_idx):
            print(f"Warning: Could not determine best design for {week_str}, skipping...")
            continue
            
        # Get all designs with best score
        best_score = summary_table.loc[best_score_idx, combined_score_col]
        best_designs = summary_table[summary_table[combined_score_col] == best_score]['design_id'].tolist()
        
        comparison_data.append({
            'test_length': week_str,
            'best_mde_score': summary_table[f'mde_score_{week_str}'].max(),
            'avg_mde_score': summary_table[f'mde_score_{week_str}'].mean(),
            'best_balance_score': summary_table[f'balance_score_norm_{week_str}'].max(),
            'avg_balance_score': summary_table[f'balance_score_norm_{week_str}'].mean(),
            'best_combined_score': best_score,
            'avg_combined_score': summary_table[combined_score_col].mean(),
            'best_design': best_designs[0] if best_designs else None,
            'best_designs': best_designs
        })
    
    if not comparison_data:
        raise ValueError("No valid data found for any test length")
        
    comparison = pd.DataFrame(comparison_data)
    
    # Create visualization
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(20, 5))
    
    # Plot MDE/Power comparison
    comparison.plot(x='test_length', y=['best_mde_score', 'avg_mde_score'], kind='bar', ax=ax1)
    ax1.set_title('MDE/Power Score Comparison')
    ax1.set_ylabel('MDE/Power Score (normalized)')
    
    # Plot balance score comparison
    comparison.plot(x='test_length', y=['best_balance_score', 'avg_balance_score'], kind='bar', ax=ax2)
    ax2.set_title('Balance Score Comparison')
    ax2.set_ylabel('Balance Score (normalized)')
    
    # Plot combined score comparison
    comparison.plot(x='test_length', y=['best_combined_score', 'avg_combined_score'], kind='bar', ax=ax3)
    ax3.set_title('Combined Score Comparison')
    ax3.set_ylabel('Combined Score')
    
    plt.tight_layout()
    
    mlflow.log_figure(fig, "test_length_comparison.png")
    mlflow.log_table(comparison, "test_length_comparison.json")
    plt.close()
    
    return comparison

def create_best_designs_summary(summary_table, week_str, score_weights):
    """
    Create a summary of the best designs based on different metrics.
    
    Parameters:
    -----------
    summary_table : pandas.DataFrame
        Summary table containing design metrics and scores
    week_str : str
        Test length string (e.g., '8wk')
    score_weights : dict
        Dictionary containing weights for MDE and balance scores
        
    Returns:
    --------
    pandas.DataFrame
        Summary table of best designs with their scores
    """
    # Validate input
    if summary_table.empty:
        raise ValueError("summary_table is empty")
    
    # Get number of test groups
    n_test_groups = len(summary_table) // len(summary_table['design_id'].unique())
    
    # Get best designs for each metric
    best_mde_designs = summary_table[summary_table[f'mde_rank_{week_str}'] == 1]
    best_balance_designs = summary_table[summary_table[f'balance_rank_{week_str}'] == 1]
    best_combined_designs = summary_table[summary_table[f'combined_rank_{week_str}'] == 1]

    # For single test group case, simplify the output
    if n_test_groups == 1:
        best_designs_summary = pd.DataFrame({
            'Aspect': ['MDE', 'Balance', 'Combined'],
            'Best Design(s)': [
                ', '.join(map(str, best_mde_designs['design_id'].unique())),
                ', '.join(map(str, best_balance_designs['design_id'].unique())),
                ', '.join(map(str, best_combined_designs['design_id'].unique()))
            ],
            'Score': [
                best_mde_designs[f'mde_score_{week_str}'].iloc[0],
                best_balance_designs[f'balance_score_norm_{week_str}'].iloc[0],
                best_combined_designs[f'combined_score_{week_str}'].iloc[0]
            ],
            'MDE (%)': [
                f"{best_mde_designs[f'mde_percent_{week_str}_mean'].iloc[0]:.2f}%",
                f"{best_balance_designs[f'mde_percent_{week_str}_mean'].iloc[0]:.2f}%",
                f"{best_combined_designs[f'mde_percent_{week_str}_mean'].iloc[0]:.2f}%"
            ],
            'Test Group %': [
                f"{best_mde_designs['test_group_percentage_mean'].iloc[0]:.2f}%",
                f"{best_balance_designs['test_group_percentage_mean'].iloc[0]:.2f}%",
                f"{best_combined_designs['test_group_percentage_mean'].iloc[0]:.2f}%"
            ]
        })
    else:
        # Create summary DataFrame for multiple test groups
        best_designs_summary = pd.DataFrame({
            'Aspect': ['MDE', 'Balance', 'Combined'],
            'Best Design(s)': [
                ', '.join(map(str, best_mde_designs['design_id'].unique())),
                ', '.join(map(str, best_balance_designs['design_id'].unique())),
                ', '.join(map(str, best_combined_designs['design_id'].unique()))
            ],
            'Score': [
                best_mde_designs[f'mde_score_{week_str}'].iloc[0],
                best_balance_designs[f'balance_score_norm_{week_str}'].iloc[0],
                best_combined_designs[f'combined_score_{week_str}'].iloc[0]
            ],
            'Other Scores': [
                f"MDE: {best_mde_designs[f'mde_score_{week_str}'].iloc[0]:.3f}, "
                f"Balance: {best_mde_designs[f'balance_score_norm_{week_str}'].iloc[0]:.3f}",
                f"MDE: {best_balance_designs[f'mde_score_{week_str}'].iloc[0]:.3f}, "
                f"Balance: {best_balance_designs[f'balance_score_norm_{week_str}'].iloc[0]:.3f}",
                f"MDE: {best_combined_designs[f'mde_score_{week_str}'].iloc[0]:.3f}, "
                f"Balance: {best_combined_designs[f'balance_score_norm_{week_str}'].iloc[0]:.3f}"
            ],
            'Score Weights': [
                f"MDE: {score_weights['mde']*100:.0f}%, Balance: {score_weights['balance']*100:.0f}%",
                f"MDE: {score_weights['mde']*100:.0f}%, Balance: {score_weights['balance']*100:.0f}%",
                f"MDE: {score_weights['mde']*100:.0f}%, Balance: {score_weights['balance']*100:.0f}%"
            ]
        })
    
    return best_designs_summary

def generate_test_length_report(design_summary, summary_table, week_str, n_designs, n_test_grps, score_weights):
    """
    Generate a detailed report for a specific test length.
    
    Parameters:
    -----------
    design_summary : pandas.DataFrame
        DataFrame containing design metrics
    summary_table : pandas.DataFrame
        Summary table for the test length
    week_str : str
        Test length string (e.g., '8wk')
    n_designs : int
        Number of designs
    n_test_grps : int
        Number of test groups per design
    score_weights : dict
        Dictionary containing weights for MDE and balance scores
        
    Returns:
    --------
    str
        Markdown formatted report
    """
    # Validate input
    if design_summary.empty or summary_table.empty:
        raise ValueError("Input DataFrames cannot be empty")
    
    if n_designs <= 0 or n_test_grps <= 0:
        raise ValueError("n_designs and n_test_grps must be positive integers")
    
    # Get best designs for each metric
    best_mde_designs = summary_table[summary_table[f'mde_rank_{week_str}'] == 1]
    best_balance_designs = summary_table[summary_table[f'balance_rank_{week_str}'] == 1]
    best_combined_designs = summary_table[summary_table[f'combined_rank_{week_str}'] == 1]

    # Get design IDs with validation
    best_mde_design_ids = best_mde_designs['design_id'].unique().tolist() if not best_mde_designs.empty else []
    best_balance_design_ids = best_balance_designs['design_id'].unique().tolist() if not best_balance_designs.empty else []
    best_combined_design_ids = best_combined_designs['design_id'].unique().tolist() if not best_combined_designs.empty else []

    # Create report
    report = (
        f"# Design Comparison Report - {week_str}\n\n"
        f"## Overview\n"
        f"- Number of Designs: {n_designs}\n"
        f"- Number of Test Groups per Design: {n_test_grps}\n"
        f"- Average |MDE|: {design_summary[f'mde_percent_{week_str}'].apply(builtins.abs).mean():.3f}%\n\n"
    )

    # Add test group specific information for multiple test groups
    if n_test_grps > 1:
        report += (
            f"## Test Group Analysis\n"
            f"- Average Test Group Size: {design_summary['test_group_percentage'].mean():.1f}%\n"
            f"- Test Group Size Variability: {design_summary['test_group_percentage'].std():.1f}%\n"
            f"- Control Group Size: {design_summary['control_group_percentage'].mean():.1f}%\n\n"
        )

    # Best Design Analysis Section
    report += (
        f"## Best Design Analysis\n"
        f"### Top Design{'s' if len(best_combined_design_ids) > 1 else ''} (Combined Score)\n"
    )

    # Combined Score Section
    if not best_combined_design_ids:
        report += "No designs found with combined score ranking.\n"
    elif len(best_combined_design_ids) > 1:
        report += (
            f"- Multiple designs tied for best combined score (Designs {', '.join(map(str, best_combined_design_ids))})\n"
            f"- All tied designs achieved the same combined score: {best_combined_designs[f'combined_score_{week_str}'].iloc[0]:.3f}\n"
        )
    else:
        report += (
            f"- Design {best_combined_design_ids[0]}\n"
            f"- Combined Score: {best_combined_designs[f'combined_score_{week_str}'].iloc[0]:.3f}\n"
        )

    # MDE Analysis Section
    report += (
        f"\n### MDE Analysis\n"
        f"Best MDE Design{'s' if len(best_mde_design_ids) > 1 else ''}:\n"
    )

    if not best_mde_design_ids:
        report += "No designs found with MDE ranking.\n"
    elif len(best_mde_design_ids) > 1:
        report += (
            f"- Multiple designs tied for best MDE (Designs {', '.join(map(str, best_mde_design_ids))})\n"
            f"- All tied designs achieved the same MDE score: {best_mde_designs[f'mde_score_{week_str}'].iloc[0]:.3f}\n"
        )
    else:
        report += (
            f"- Design {best_mde_design_ids[0]}\n"
            f"- MDE Score: {best_mde_designs[f'mde_score_{week_str}'].iloc[0]:.3f}\n"
            f"- MDE Value: {best_mde_designs[f'mde_percent_{week_str}_mean'].iloc[0]:.3f}%\n"
        )

    # Balance Analysis Section
    report += (
        f"\n### Balance Analysis\n"
        f"Best Balanced Design{'s' if len(best_balance_design_ids) > 1 else ''}:\n"
    )

    if not best_balance_design_ids:
        report += "No designs found with balance ranking.\n"
    elif len(best_balance_design_ids) > 1:
        report += (
            f"- Multiple designs tied for best balance (Designs {', '.join(map(str, best_balance_design_ids))})\n"
            f"- All tied designs achieved the same balance score: {best_balance_designs[f'balance_score_norm_{week_str}'].iloc[0]:.3f}\n"
        )
    else:
        report += (
            f"- Design {best_balance_design_ids[0]}\n"
            f"- Balance Score: {best_balance_designs[f'balance_score_norm_{week_str}'].iloc[0]:.3f}\n"
            f"- Test Group Size: {best_balance_designs['test_group_percentage_mean'].iloc[0]:.1f}%\n"
        )

    # Design Rankings Section
    report += (
        "\n## Design Rankings\n"
    )
    
    if best_combined_design_ids:
        report += f"1. Best Combined Score: Design{'s' if len(best_combined_design_ids) > 1 else ''} {', '.join(map(str, best_combined_design_ids))}\n"
    else:
        report += "1. Best Combined Score: No designs found\n"
        
    if best_mde_design_ids:
        report += f"2. Best MDE: Design{'s' if len(best_mde_design_ids) > 1 else ''} {', '.join(map(str, best_mde_design_ids))}\n"
    else:
        report += "2. Best MDE: No designs found\n"
        
    if best_balance_design_ids:
        report += f"3. Best Balance: Design{'s' if len(best_balance_design_ids) > 1 else ''} {', '.join(map(str, best_balance_design_ids))}\n"
    else:
        report += "3. Best Balance: No designs found\n"
    
    # Create Best Designs Summary using the dedicated function
    try:
        best_designs_summary = create_best_designs_summary(summary_table, week_str, score_weights)
        report += "\n## Best Designs Summary\n"
        report += "This table provides a comprehensive comparison of the top-performing designs across all metrics:\n"
        report += f"{best_designs_summary.to_markdown()}\n\n"
    except Exception as e:
        report += "\n## Best Designs Summary\n"
        report += f"Unable to generate best designs summary: {str(e)}\n\n"
    
    # Add score weights section
    report += (
        f"\n## Score Weights\n"
        f"- MDE: {score_weights['mde']*100:.0f}%\n"
        f"- Balance: {score_weights['balance']*100:.0f}%\n\n"
    )
    
    return report

def generate_overall_report(test_length_comparison, score_weights):
    """
    Generate an overall report comparing designs across test lengths.
    
    Parameters:
    -----------
    test_length_comparison : pandas.DataFrame
        Comparison table with metrics across test lengths
    score_weights : dict
        Dictionary containing weights for MDE and balance scores
        
    Returns:
    --------
    str
        Markdown formatted report
    """
    # Validate input
    if test_length_comparison.empty:
        raise ValueError("test_length_comparison DataFrame is empty")
    
    # Check if we have a single test length
    is_single_test_length = len(test_length_comparison) == 1
    
    # Create overall summary report
    overall_report = (
        f"# Overall Design Comparison Report\n\n"
        f"## Test Length Analysis\n"
        f"{test_length_comparison.to_markdown()}\n\n"
    )

    if is_single_test_length:
        # Simplified report for single test length
        test_length = test_length_comparison['test_length'].iloc[0]
        overall_report += (
            f"## Single Test Length Analysis ({test_length})\n"
            f"### Best Performing Design\n"
            f"- Design: {test_length_comparison['best_design'].iloc[0]}\n"
            f"- Combined Score: {test_length_comparison['best_combined_score'].iloc[0]:.3f}\n"
            f"- MDE Score: {test_length_comparison['best_mde_score'].iloc[0]:.3f}\n"
            f"- Balance Score: {test_length_comparison['best_balance_score'].iloc[0]:.3f}\n\n"
            
            f"### Average Performance\n"
            f"- Average Combined Score: {test_length_comparison['avg_combined_score'].iloc[0]:.3f}\n"
            f"- Average MDE Score: {test_length_comparison['avg_mde_score'].iloc[0]:.3f}\n"
            f"- Average Balance Score: {test_length_comparison['avg_balance_score'].iloc[0]:.3f}\n\n"
        )
    else:
        # Handle ties in best test length
        best_test_lengths = test_length_comparison[
            test_length_comparison['best_combined_score'] == 
            test_length_comparison['best_combined_score'].max()
        ]
        
        overall_report += "## Key Recommendations\n"
        if len(best_test_lengths) > 1:
            overall_report += (
                f"1. Best Overall Test Length{'s' if len(best_test_lengths) > 1 else ''}: "
                f"{', '.join(best_test_lengths['test_length'].tolist())}\n"
                f"   (Multiple test lengths tied for best combined score)\n"
            )
        else:
            overall_report += (
                f"1. Best Overall Test Length: "
                f"{test_length_comparison.loc[test_length_comparison['best_combined_score'].idxmax(), 'test_length']}\n"
            )

        # Handle ties in most consistent design
        most_consistent_designs = test_length_comparison['best_designs'].explode().mode()
        if len(most_consistent_designs) > 1:
            overall_report += (
                f"2. Most Consistent Design{'s' if len(most_consistent_designs) > 1 else ''}: "
                f"Design{'s' if len(most_consistent_designs) > 1 else ''} {', '.join(map(str, most_consistent_designs))}\n"
                f"   (Multiple designs showed consistent performance across test lengths)\n\n"
            )
        else:
            overall_report += (
                f"2. Most Consistent Design: Design {test_length_comparison['best_design'].mode().iloc[0]}\n\n"
            )

    # Performance Summary Section (common for both single and multiple test lengths)
    overall_report += (
        f"## Performance Summary\n"
        f"- Best Combined Score: {test_length_comparison['best_combined_score'].max():.3f}\n"
        f"- Average Combined Score: {test_length_comparison['avg_combined_score'].mean():.3f}\n"
        f"- Best MDE Score: {test_length_comparison['best_mde_score'].max():.3f}\n"
        f"- Best Balance Score: {test_length_comparison['best_balance_score'].max():.3f}\n\n"
        
        f"## Score Weights and Interpretation\n"
        f"- MDE: {score_weights['mde']*100:.0f}% (Sensitivity to detect effects)\n"
        f"- Balance: {score_weights['balance']*100:.0f}% (Group distribution)\n\n"
    )

    if not is_single_test_length:
        overall_report += (
            f"## Key Insights\n"
            f"1. The best test length{'s' if len(best_test_lengths) > 1 else ''} provide{'s' if len(best_test_lengths) == 1 else ''} "
            f"optimal balance between MDE and Balance\n"
            f"2. Consider both peak and average performance when selecting a test length\n"
            f"3. Designs that perform consistently across test lengths are more reliable\n\n"
            
            f"## Analysis Guidelines\n"
            f"1. MDE Analysis:\n"
            f"   - Look for designs with low average |MDE|\n"
            f"   - Check for consistency across test groups\n"
            f"   - Consider the practical significance of the MDE values\n"
            f"   - Note that multiple designs may achieve similar MDE scores\n\n"
            f"2. Balance Analysis:\n"
            f"   - Aim for 50/50 test/control split\n"
            f"   - Monitor test group size variability\n"
            f"   - Consider practical constraints on group sizes\n"
            f"   - Multiple designs may achieve similar balance scores\n\n"
            f"3. Combined Score:\n"
            f"   - Weights reflect relative importance of each metric\n"
            f"   - Higher scores indicate better overall design\n"
            f"   - Consider trade-offs between metrics\n"
            f"   - Multiple designs may achieve similar combined scores\n"
        )

    # Add a section about handling ties
    overall_report += (
        "\n## Note on Tied Scores\n"
        "When multiple designs achieve the same score for any metric (MDE, Balance, or Combined):\n"
        "- All tied designs are considered equally good for that metric\n"
        "- The report shows all tied designs to help in decision making\n"
        "- Consider other factors (like implementation complexity) when choosing between tied designs\n"
        "- Ties may occur at different test lengths, indicating consistent performance\n"
    )
    
    return overall_report

def generate_cv_fit_plots(
    data: pd.DataFrame,
    kpi: str,
    market_assignments_df: pd.DataFrame,
    indexes: List[List[int]] = None,
    date_col: str = 'date',
    geo_col: str = 'geo',
    n_splits: int = 5,
    random_state: int = None
) -> Dict[str, Dict[str, Any]]:
    """
    Generate cross-validation based fit plots to assess synthetic control model performance
    for different test designs.

    Parameters
    ----------
    data : pd.DataFrame
        Long format dataframe containing the data. Must include date_col, geo_col, and kpi columns.
    kpi : str
        Name of the KPI column to analyze.
    market_assignments_df : pd.DataFrame
        DataFrame containing test and control groups for each index. Must have columns
        'test_dmas' and 'control_dmas'.
    indexes : List[List[int]], optional
        List of design candidates, where each design is a list of indices corresponding
        to positions in market_assignments_df after reset_index(). If not provided, designs
        will be automatically grouped by control groups.
    date_col : str, default='date'
        Name of the date column in the data.
    geo_col : str, default='geo'
        Name of the geographic unit column in the data.
    n_splits : int, default=5
        Number of cross-validation folds to use.
    random_state : int, optional
        Random seed for reproducibility.

    Returns
    -------
    Dict[str, Dict[str, Any]]
        Dictionary containing results for each design, including metrics and fold information.
    """
    # Input validation
    required_cols = [date_col, geo_col, kpi]
    if not all(col in data.columns for col in required_cols):
        raise ValueError(f"data must contain columns: {required_cols}")
    
    if not all(col in market_assignments_df.columns for col in ['test_dmas', 'control_dmas']):
        raise ValueError("market_assignments_df must contain columns: 'test_dmas', 'control_dmas'")
    
    if n_splits < 2:
        raise ValueError("n_splits must be at least 2")
    
    if data.empty:
        raise ValueError("data DataFrame is empty")
    
    if market_assignments_df.empty:
        raise ValueError("market_assignments_df DataFrame is empty")

    # Ensure date column is datetime
    try:
        data[date_col] = pd.to_datetime(data[date_col])
    except Exception as e:
        raise ValueError(f"Could not convert {date_col} to datetime: {e}")

    # Reset index of market_assignments_df to ensure consistent indexing
    market_assignments_df = market_assignments_df.reset_index(drop=True)

    # If indexes is not provided, create indexes by grouping by control groups
    if indexes is None:
        # Group market assignments by control groups to identify designs
        control_groups = market_assignments_df['control_dmas'].apply(lambda x: tuple(sorted(x)))
        unique_control_groups = control_groups.unique()
        
        # Create indexes for each unique control group
        indexes = []
        for control_group in unique_control_groups:
            # Get all rows that share this control group
            design_indices = market_assignments_df[control_groups == control_group].index.tolist()
            if design_indices:  # Only add if we found matching indices
                indexes.append(design_indices)
        
        if not indexes:
            raise ValueError("No valid designs found in market_assignments_df")
    else:
        # Validate that all indexes are within bounds
        max_idx = len(market_assignments_df) - 1
        for design_idx, indices in enumerate(indexes):
            if not all(0 <= idx <= max_idx for idx in indices):
                raise ValueError(
                    f"Design {design_idx} contains invalid indices. "
                    f"All indices must be between 0 and {max_idx}"
                )

    # Check for single test group case
    is_single_test_group = all(len(design_indices) == 1 for design_indices in indexes)
    if is_single_test_group:
        print("Note: Running analysis with single test group per design")

    def _format_date(date) -> str:
        """Format date to string in YYYY-MM-DD format."""
        if isinstance(date, pd.Timestamp):
            return date.strftime('%Y-%m-%d')
        return str(date)

    def _calculate_metrics(actuals: np.ndarray, predictions: np.ndarray) -> Dict[str, float]:
        """Calculate performance metrics for a single fold."""
        if len(actuals) == 0 or len(predictions) == 0:
            raise ValueError("Empty arrays provided for metric calculation")
        
        # Calculate scale information
        actuals_mean = actuals.mean()
        actuals_std = actuals.std()
        actuals_abs_sum = builtins.abs(actuals).sum()
        
        # Standard metrics
        mae = builtins.abs(actuals - predictions).mean()
        rmse = np.sqrt(((actuals - predictions) ** 2).mean())
        
        # Scale-independent metrics
        mae_normalized_by_mean = mae / builtins.abs(actuals_mean) if actuals_mean != 0 else np.nan
        rmse_normalized_by_mean = rmse / builtins.abs(actuals_mean) if actuals_mean != 0 else np.nan
        mae_normalized_by_std = mae / actuals_std if actuals_std != 0 else np.nan
        rmse_normalized_by_std = rmse / actuals_std if actuals_std != 0 else np.nan
        
        # Percentage errors
        mae_percentage = (mae / builtins.abs(actuals_mean)) * 100 if actuals_mean != 0 else np.nan
        rmse_percentage = (rmse / builtins.abs(actuals_mean)) * 100 if actuals_mean != 0 else np.nan
        
        return {
            'MAE': mae,
            'RMSE': rmse,
            'R2': 1 - (((actuals - predictions) ** 2).sum() / 
                      ((actuals - actuals.mean()) ** 2).sum()),
            'Normalized Residual': builtins.abs(actuals - predictions).sum() / actuals_abs_sum,
            # Scale-independent versions
            'MAE_Normalized_By_Mean': mae_normalized_by_mean,
            'RMSE_Normalized_By_Mean': rmse_normalized_by_mean,
            'MAE_Normalized_By_Std': mae_normalized_by_std,
            'RMSE_Normalized_By_Std': rmse_normalized_by_std,
            'MAE_Percentage': mae_percentage,
            'RMSE_Percentage': rmse_percentage,
            # Scale information for context
            'Target_Mean': actuals_mean,
            'Target_Std': actuals_std
        }

    def _create_visualization(
        design_name: str,
        cv_metrics: List[Dict[str, float]],
        avg_metrics: Dict[str, float],
        is_single_test_group: bool = False
    ) -> Tuple[plt.Figure, plt.Axes]:
        """Create visualization for a single design's CV results."""
        # Create figure with subplots for each metric group
        fig, axes = plt.subplots(3, 2, figsize=(15, 18))
        fig.suptitle(f'Cross-Validation Metrics for {design_name}', fontsize=16, y=0.95)
        
        # Convert CV metrics to DataFrame
        metrics_df = pd.DataFrame(cv_metrics)
        
        # Plot each metric group
        metric_groups = [
            ['MAE', 'RMSE'],  # Raw metrics
            ['MAE_Normalized_By_Std', 'RMSE_Normalized_By_Std'],  # Normalized by std
            ['MAE_Normalized_By_Mean', 'RMSE_Normalized_By_Mean']  # Normalized by mean
        ]
        
        for row, (metric1, metric2) in enumerate(metric_groups):
            for col, metric in enumerate([metric1, metric2]):
                ax = axes[row, col]
                
                if metric in metrics_df.columns:
                    # Box plot
                    metrics_df.boxplot(column=metric, ax=ax)
                    ax.set_title(f'{metric} Distribution')
                    ax.set_ylabel('Value')
                    ax.grid(True, alpha=0.3)
                    
                    # Add individual points
                    ax.scatter([1] * len(metrics_df), metrics_df[metric], alpha=0.5, color='red')
                    
                    # Add average line
                    if metric in avg_metrics:
                        avg_value = avg_metrics[metric]
                        ax.axhline(y=avg_value, color='green', linestyle='--', 
                                label=f'Average: {avg_value:.3f}')
                    
                    # Add fold numbers
                    for i, value in enumerate(metrics_df[metric]):
                        ax.text(1.1, value, f'Fold {i+1}', fontsize=8)
                    
                    ax.legend()
                else:
                    ax.text(0.5, 0.5, f'{metric}\nNot Available', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(f'{metric}')
        
        # Add note for single test group case
        if is_single_test_group:
            fig.text(0.5, 0.01, 
                    "Note: Single test group analysis - results may be less robust than multi-group analysis",
                    ha='center', fontsize=10, style='italic')
        
        plt.tight_layout()
        return fig, axes

    results = {}
    
    # Process each design
    for design_idx, design_candidate in enumerate(sorted(indexes)):
        control_gmas = market_assignments_df.reset_index().loc[design_candidate[0], 'control_dmas']
        
        for idx, test_group_idx in enumerate(design_candidate):
            test_gmas = market_assignments_df.reset_index().loc[test_group_idx, 'test_dmas']
            design_name = f"Design_{design_idx}_TestGroup_{idx}"
            
            # Get the relevant data
            design_data = data[data[geo_col].isin(test_gmas + control_gmas)].copy()
            
            # Create time-based splits
            unique_dates = sorted(design_data[date_col].unique())
            if len(unique_dates) < n_splits:
                raise ValueError(f"Not enough unique dates ({len(unique_dates)}) for {n_splits} splits")
            
            split_size = len(unique_dates) // n_splits
            splits = [unique_dates[i:i + split_size] for i in range(0, len(unique_dates), split_size)]
            
            # Perform cross-validation
            cv_metrics = []
            fold_info = []
            
            for i, test_dates in enumerate(splits):
                train_dates = [d for d in unique_dates if d not in test_dates]
                
                # Convert all dates to string format
                train_dates = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in train_dates]
                test_dates = [pd.to_datetime(d).strftime('%Y-%m-%d') for d in test_dates]
                test_start_date = test_dates[0]
                test_end_date = test_dates[-1]
                
                # Prepare data
                panel_data = long_df_to_paneldataset(
                    design_data, 
                    date_col, 
                    geo_col, 
                    kpi)
                
                train_data = panel_data.wide_data.loc[:, panel_data.wide_data.columns.isin(train_dates)]   
                test_data = panel_data.wide_data.loc[:, panel_data.wide_data.columns.isin(test_dates)]

                pds = PanelDataset(pd.concat([train_data, test_data], axis=1), 
                                 treated_units=test_gmas,
                                 treated_periods=[TimePeriod(test_start_date, test_end_date)] * len(test_gmas))

                pds.wide_data.fillna(0, inplace=True)

                model = TBRRidge(full_model=False, inference=None)
                model.run_analysis(pds)

                start = pds.treated_start_idxs[0]
                end = pds.treated_end_idxs[0]
                
                # Get actuals and predictions for test period
                test_actuals = model.results["y"][start:end]
                test_predictions = model.results['y_hat'][start:end]
                
                # Calculate metrics for this fold
                fold_metrics = _calculate_metrics(test_actuals, test_predictions)
                cv_metrics.append(fold_metrics)
                
                # Store fold information
                fold_info.append({
                    'fold_idx': i,
                    'train_dates': [_format_date(d) for d in train_dates],
                    'test_dates': [_format_date(d) for d in test_dates],
                    'test_start_date': test_start_date,
                    'test_end_date': test_end_date,
                    'train_size': len(train_dates),
                    'test_size': len(test_dates)
                })
            
            # Calculate average metrics across folds
            avg_metrics = {
                metric: np.mean([fold[metric] for fold in cv_metrics])
                for metric in ['MAE', 'RMSE', 'R2', 'Normalized Residual', 
                             'MAE_Percentage', 'RMSE_Percentage', 
                             'MAE_Normalized_By_Mean', 'RMSE_Normalized_By_Mean',
                             'MAE_Normalized_By_Std', 'RMSE_Normalized_By_Std',
                             'Target_Mean', 'Target_Std']
                if metric in cv_metrics[0]  # Only include if metric exists
            }
            
            # Create visualization
            fig, _ = _create_visualization(design_name, cv_metrics, avg_metrics, is_single_test_group)
            
            # Create summary row for the table
            summary_row = {
                'Design': design_name,
                'Test Markets': ', '.join(map(str, test_gmas)),
                'Control Markets': ', '.join(map(str, control_gmas)),
                'Target_Mean': avg_metrics.get('Target_Mean', np.nan),
                'Target_Std': avg_metrics.get('Target_Std', np.nan),
                'MAE': avg_metrics.get('MAE', np.nan),
                'RMSE': avg_metrics.get('RMSE', np.nan),
                'MAE_Percentage': avg_metrics.get('MAE_Percentage', np.nan),
                'RMSE_Percentage': avg_metrics.get('RMSE_Percentage', np.nan),
                'MAE_Normalized_By_Mean': avg_metrics.get('MAE_Normalized_By_Mean', np.nan),
                'RMSE_Normalized_By_Mean': avg_metrics.get('RMSE_Normalized_By_Mean', np.nan),
                'R2': avg_metrics.get('R2', np.nan),
                'Normalized_Residual': avg_metrics.get('Normalized Residual', np.nan)
            }
            
            # Store results
            results[design_name] = {
                'figure': fig,
                'metrics': avg_metrics,
                'cv_metrics': cv_metrics,
                'fold_info': fold_info,
                'test_markets': test_gmas,
                'control_markets': control_gmas,
                'design_idx': design_idx,
                'test_group_idx': test_group_idx,
                'summary_row': summary_row,
                'is_single_test_group': is_single_test_group
            }
    
    # Create summary table
    summary_df = pd.DataFrame([results[design_name]['summary_row'] for design_name in results.keys()])
    results['summary_table'] = summary_df
    
    return results

def log_cv_fit_results(results: Dict[str, Dict[str, Any]], run_name: str = "cv_fit_analysis"):
    """
    Log cross-validation fit results to MLflow, with best performing designs calculated
    by averaging metrics across test groups.
    
    Parameters
    ----------
    results : Dict[str, Dict[str, Any]]
        Results dictionary from generate_cv_fit_plots
    run_name : str, default="cv_fit_analysis"
        Name for the MLflow run
    """
    import mlflow
    from collections import defaultdict
    import pandas as pd
    import numpy as np
    import matplotlib.pyplot as plt
    
    with mlflow.start_run(run_name=run_name, nested=True):
        # Log the summary table
        summary_df = results['summary_table']
        mlflow.log_table(data=summary_df, artifact_file="cv_fit_metrics.json")
        
        # Calculate average metrics by design (across test groups)
        design_metrics = defaultdict(lambda: defaultdict(list))
        for design_name, design_results in results.items():
            if design_name == 'summary_table':
                continue
            
            # Extract design number from name (e.g., "Design_0_TestGroup_1" -> "Design_0")
            design_base = '_'.join(design_name.split('_')[:2])
            
            # Collect metrics for this test group
            for metric, value in design_results['metrics'].items():
                design_metrics[design_base][metric].append(value)
        
        # Calculate averages for each design
        design_avg_metrics = {}
        for design, metrics in design_metrics.items():
            design_avg_metrics[design] = {
                metric: np.mean(values) for metric, values in metrics.items()
            }
        
        # Convert to DataFrame for easier analysis
        design_avg_df = pd.DataFrame.from_dict(design_avg_metrics, orient='index')
        design_avg_df.index.name = 'Design'
        design_avg_df.reset_index(inplace=True)
        
        # Log the design averages table
        mlflow.log_table(data=design_avg_df, artifact_file="cv_fit_design_averages.json")
        
        # Generate and log a markdown report with design averages
        report = f"""# Cross-Validation Fit Analysis Report

## Summary Statistics by Test Group
{summary_df.to_markdown()}

## Average Performance by Design (Across Test Groups)
{design_avg_df.to_markdown()}

## Best Performing Designs (Averaged Across Test Groups)
- Best R²: {design_avg_df.loc[design_avg_df['R2'].idxmax(), 'Design']} (R² = {design_avg_df['R2'].max():.3f})
- Best MAE: {design_avg_df.loc[design_avg_df['MAE'].idxmin(), 'Design']} (MAE = {design_avg_df['MAE'].min():.3f})
- Best RMSE: {design_avg_df.loc[design_avg_df['RMSE'].idxmin(), 'Design']} (RMSE = {design_avg_df['RMSE'].min():.3f})

## Interpretation Guidelines
- R² > 0.8: Excellent fit
- R² 0.6-0.8: Good fit
- R² 0.4-0.6: Moderate fit
- R² < 0.4: Poor fit

## Design Details (Averaged Across Test Groups)
"""
        for design, metrics in design_avg_metrics.items():
            report += f"\n### {design}\n"
            report += "- Average Metrics:\n"
            for metric, value in metrics.items():
                report += f"  - {metric}: {value:.3f}\n"
            
            # Add test group details
            test_groups = [k for k in results.keys() if k.startswith(design) and k != 'summary_table']
            report += "\nTest Groups:\n"
            for test_group in test_groups:
                group_results = results[test_group]
                report += f"- {test_group}:\n"
                report += f"  - Test Markets: {', '.join(map(str, group_results['test_markets']))}\n"
                report += f"  - Control Markets: {', '.join(map(str, group_results['control_markets']))}\n"
                for metric, value in group_results['metrics'].items():
                    report += f"  - {metric}: {value:.3f}\n"
        
        mlflow.log_text(report, "cv_fit_report.md")
        
        # Log individual design plots
        for design_name, design_results in results.items():
            if design_name == 'summary_table':
                continue
            mlflow.log_figure(design_results['figure'], f"cv_fit_{design_name}.png")
        
        # Create and log a bar plot comparing average metrics across designs
        fig, axes = plt.subplots(3, 2, figsize=(20, 18))
        fig.suptitle('Average Metrics by Design (Across Test Groups)', fontsize=16)
        
        # Define metric groups for plotting
        metric_groups = [
            ['MAE', 'RMSE'],  # Raw metrics
            ['MAE_Normalized_By_Std', 'RMSE_Normalized_By_Std'],  # Normalized by std
            ['MAE_Normalized_By_Mean', 'RMSE_Normalized_By_Mean']  # Normalized by mean
        ]
        
        for row, (metric1, metric2) in enumerate(metric_groups):
            for col, metric in enumerate([metric1, metric2]):
                ax = axes[row, col]
                
                if metric in design_avg_df.columns:
                    # Sort designs by metric value
                    ascending = metric in ['MAE', 'RMSE', 'MAE_Percentage', 'RMSE_Percentage', 
                                        'MAE_Normalized_By_Mean', 'RMSE_Normalized_By_Mean']
                    sorted_designs = design_avg_df.sort_values(by=metric, ascending=ascending)
                    
                    # Create bar plot
                    bars = ax.bar(sorted_designs['Design'], sorted_designs[metric])
                    
                    # Add value labels
                    for bar in bars:
                        height = bar.get_height()
                        if not np.isnan(height):
                            ax.text(bar.get_x() + bar.get_width()/2., height,
                                   f'{height:.3f}',
                                   ha='center', va='bottom' if metric == 'R2' else 'top')
                    
                    ax.set_title(f'Average {metric} by Design')
                    ax.set_xticklabels(sorted_designs['Design'], rotation=45, ha='right')
                    ax.grid(True, alpha=0.3)
                else:
                    ax.text(0.5, 0.5, f'{metric}\nNot Available', 
                           ha='center', va='center', transform=ax.transAxes)
                    ax.set_title(f'Average {metric} by Design')
        
        plt.tight_layout()
        mlflow.log_figure(fig, "cv_fit_design_comparison.png")