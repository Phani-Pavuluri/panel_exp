import requests 
import json 
import numpy as np 
import pandas as pd 

from typing import NewType

url = NewType('url', str)



def post_power_curve(  API_HOST: url
					 , pdf: pd.DataFrame
					 , test_id: int
					 , kpi: str
					 , cloud: str) -> str:
	"""Function to post power curve to web database. 

	Args:
		API_HOST (url): URL for API host
		pdf (pd.DataFrame): Power Curve DataFrame
		test_id (int): Unique ID for test.
		kpi (str): KPI the power curve is for. 
		cloud (str): What cloud is this related to can be: CC, DC, DMe

	Returns:
		str: Return Response Message from API. 
	"""
 
	url = "{}/api/testdb/data/{}/power_raw/{}/{}".format(API_HOST, test_id, kpi.lower(), cloud.lower())
	d = pdf.to_dict()
	response = requests.request("POST", url, json=d )
	return response.text 



def post_power_results(API_HOST: url
					   , test_id: int
					   , cloud: str
					   , kpi: str
					   , pa ) -> str:
	"""Function to post pre-test analysis details to web database.


	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.
		cloud (str):  What cloud is this related to can be: CC, DC, DMe
		kpi (str): KPI the power curve is for. 
		pa (_type_): _description_

	Returns:
		str: _description_
	"""
	d = {"test_id" : test_id , 
		"cloud" : cloud, 
		"kpi" : kpi , 
		"model": pa.model.__name__ , 
		"inference" : pa.inference , 
		"test_length" : pa.test_length , 
		"n_sim" : pa.n_simulations , 
		"mde_percent": np.abs(pa.mde_percent) , 
		"mde_kpi" : np.abs(pa.mde_kpi_cumulative) , 
		"power" : pa.power , 
		"type_1_error" : (1-pa.output_df[pa.output_df.t_effect==0].cum_ss.mean()) }
 
	url = "{API_HOST}/api/testdb/data/pretest".format(API_HOST=API_HOST)

	response = requests.request("POST", url, json=d )
	
	return response.text 


def post_raw_results(API_HOST: url
					 , df: pd.DataFrame
					 , test_id: int 
					 , dfv: int
					 , kpi: str
					 , cloud: str
					 , agg_func: str) -> str:
	"""
	This function will date a Pandas DataFrame and post it via API to GeoX Web App Database.
	"""
 
	url = "{API_HOST}/api/testdb/data/{test_id}/results_raw/{dfv}/{kpi}/{cloud}/{agg_func}".format(API_HOST= API_HOST ,
																								   test_id=test_id , 
																								   dfv=dfv, 
																								   kpi=kpi.lower(), 
																								   cloud=cloud.lower(), 
																								   agg_func=agg_func.lower())
		
	d = df.to_dict()
	response = requests.request("POST", url, json=d )
	return response.text 



def getAllTests(API_HOST: url) -> json:
	"""_summary_

	Args:
		API_HOST (url): URL for API host

	Returns:
		json: _description_
	"""
	
	url="{}/api/testdb".format(API_HOST)
	r = requests.get(url)
	return r.json()

def getSpecificTest(API_HOST: url
					, test_id: int) -> json:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.

	Returns:
		json: _description_
	"""
	
	url = "{}/api/testdb/{}".format(API_HOST, test_id)
	r = requests.get(url)
	return r.json()

def getTestDMAsasDF(API_HOST: url
					, test_id: int) -> pd.DataFrame:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.

	Returns:
		pd.DataFrame: _description_
	"""
	
	url = "{}/api/testdb/data/{}/geos".format(API_HOST, test_id)
	r = requests.get(url)
	
	df = pd.DataFrame(r.json())
	df['dma_name'] = df['info'].apply(lambda x: x['dma_name'] )
	df['dma_sales_cc'] = df['info'].apply(lambda x: x['dma_sales_cc'] )
	df['dma_sales_dc'] = df['info'].apply(lambda x: x['dma_sales_dc'] )

	return df[['dma_id', 'group', 'test_id', 'dma_name', 'dma_sales_cc', 'dma_sales_dc']]

def getPreTest(API_HOST: url
			   , test_id: int) -> json:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.

	Returns:
		json: _description_
	"""
	
	url = "{}/api/testdb/data/{}/pretest".format(API_HOST, test_id)
	r = requests.get(url)
	return r.json()

def getTestResults(API_HOST: url
				   , test_id: int):
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.

	Returns:
		_type_: _description_
	"""

	url = "{}/api/testdb/data/{}/results".format(API_HOST, test_id)
	r = requests.get(url)
	return r.json()

def getRawResFinal(API_HOST: url
				   , test_id: int
				   , cloud: str
				   , kpi: str
				   , dfv: int
				   , agg_func: str) -> pd.DataFrame:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.
		cloud (str):  What cloud is this related to can be: CC, DC, DMe
		kpi (str): Which KPI to use to pull results
		dfv (int): Version of DataFrame to pull. There are three version for three different graphs. 
		agg_func (str): How to aggregate the results. 

	Returns:
		pd.DataFrame: Returns a dataframe for Dash graphing functions. 
	"""
	
	url = "{host}/api/testdb/data/{test_id}/results_raw/{dfv}/{kpi}/{cloud}/{agg_func}".format(host = API_HOST , 
																					test_id = test_id , 
																					dfv = dfv , 
																					kpi = kpi.lower() , 
																					cloud = cloud.lower(),
																					agg_func=agg_func.lower()) 
	r = requests.get(url)

	return pd.DataFrame(json.loads(r.json()))


def getPowerCurve(API_HOST: url
				  , test_id: int
				  , kpi: str
				  , cloud: str) -> pd.DataFrame:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.
		kpi (str): _description_
		cloud (str):  What cloud is this related to can be: CC, DC, DMe

	Returns:
		pd.DataFrame: _description_
	"""
	
	url = "{host}/api/testdb/data/{test_id}/power_raw/{kpi}/{cloud}".format(host = API_HOST, test_id = test_id, kpi=kpi, cloud=cloud)
	r = requests.get(url)

	return pd.DataFrame(json.loads(r.json()))


def get_power_table(API_HOST: url
					, test_id: int) -> dict:
	"""_summary_

	Args:
		API_HOST (url): URL for API host
		test_id (int): Unique ID for test.

	Returns:
		dict: _description_
	"""
	
	url = "{API_HOST}/api/testdb/data/{test_id}/pretest".format(API_HOST=API_HOST, test_id = test_id)
	response = requests.request("GET", url )

	return dict(json.loads(response.text)[0])



def post_dmas(API_HOST: url
					 , test_id: int
					 , group: str 
					 , dma_list: list) -> str:
	"""This function will POST to the API with a list of DMAs in a specific group (test or control) and associate them with the test_id.
	
	Args:
		API_HOST (url): URL for API host
		test_id (int): Test ID associated with specific test.
		group (str): What DMAs are these test associated with (test or control).
		dma_list (list): List of DMAs in test/control group for test. 

	Returns:
		str: Return Response Message from API. 
	"""
 
	url = "{API_HOST}/api/testdb/data/add/geo".format(API_HOST= API_HOST)
 
	counter = 0 
	
	for dma in dma_list:
		data = {"dma_id": dma, "test_id": test_id, "group": group}

		response = requests.request("POST", url, json=data )
		
		print(response.status_code , response.text)
		
		if response.status_code == 201:
			counter += 1
	
	print("Successfully posted {} to GeoX Web App out of {} for {} group for test id {}".format(counter, len(dma_list), group, test_id))
	
 
def post_tab_results(  API_HOST: url
					 , df: pd.DataFrame
					 , test_id: int)  -> str:
	"""Function to post tabulated results from test. 

	Args:
		API_HOST (url): URL for API host
		tab_r (pd.DataFrame): list of lists that will be converted into a table
		test_id (int): Unique ID for test.
		kpi (str): KPI the power curve is for. 
		cloud (str): What cloud is this related to can be: CC, DC, DMe

	Returns:
		str: Return Response Message from API. 
	"""
 	
	url="{}/api/testdb/data/{}/results_tab/".format(API_HOST, test_id)
	d = df.to_dict()
	response = requests.request("POST", url, json=d )
	return response.text 


def get_tab_results(API_HOST, test_id):
    url="{}/api/testdb/data/{}/results_tab/".format(API_HOST, test_id)
    r = requests.get(url)
    df = pd.DataFrame(json.loads(r.json()))
    del df['index']
    return df