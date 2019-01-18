from flask import Flask, render_template, request
import psycopg2
import json
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup

app=Flask(__name__)
@app.route('/',methods=['GET','POST'])
def config():
	conn= psycopg2.connect(host="localhost",dbname="odk_db", user="odk_unit", password="test")
	cur= conn.cursor()
	cur.execute("SELECT \"FORM_ID\" FROM odk_db._form_info ")
	rows= cur.fetchall()
	#print (rows)
	childlist=[]
	for i in rows:
		temp=i[0]
		childlist.append(temp)	
	conn.close()
	return render_template('web.html', fdata=json.dumps(childlist))

@app.route('/getdata',methods=['POST'])
def getdata():
	if request.method=='POST':
		print ("gt a request")
		conn= psycopg2.connect(host="localhost",dbname="odk_db", user="odk_unit", password="test")
		cur1=conn.cursor()
		data=json.loads(request.data)
		# data=data.decode('utf-8')
		print (type(data),"....................................................")
		fname=data['form_name']
		cname=data['column_name']
		naka=[{'title':i} for i in cname]
		# fname= request.json['form_name']
		fname+="_core"
		fname=fname.upper()	
		# cname= request.json['column_name']
		print (cname,"asdfsdfsfdsdfsdfasdfsdfasdf")
		response=[]
		for i in cname:
			print(i)
			print("SELECT \""+i+"\" from odk_db.\""+fname+"\"")
			cur1.execute("SELECT \""+i+"\" from odk_db.\""+fname+"\"")
			values=""
			values=cur1.fetchall()
			print(values)
			data=[]
			for j in values:
				temp=j[0]
				data.append(temp)
			print (data)
			response.append(data)
		print(response)
		finallist=[]
		len_index= len(response[0])
		len_list=len(response)
		for j in range(len_index):
			innerlist=[]
			for i in range(len_list):
				innerlist.append(response[i][j])
			finallist.append(innerlist)
		print(finallist)
		finaldict={'column':naka, 'data':finallist}
		print(finaldict,"heloooooo")
		try:
			print ("return")
			return json.dumps(finaldict)
		except Exception as e:
			print(e)
			print('erroe')

@app.route('/getcolumn',methods=['POST'])
def getcolumn():
	if request.method=='POST':
		data= request.data
		data=data.decode('utf-8')
		data= data.replace("_", "-")
		data=data.upper()
		conn= psycopg2.connect(host="localhost",dbname="odk_db", user="odk_unit", password="test")
		cur= conn.cursor()
		cur.execute("SELECT \"PERSIST_AS_COLUMN_NAME\" FROM odk_db._form_data_model where REPLACE(\"PERSIST_AS_TABLE_NAME\",'_','-') like '"+data+"%'")
		rows= cur.fetchall()
		child=[]
		for j in rows:
			temp=j[0]
			child.append(temp)	
		conn.close()
		return json.dumps(child)

@app.route('/map', methods=['GET','POST'])
def mapping():
	def drop_y(df):
	    to_drop = [x for x in df if x.endswith('_y')]
	    df.drop(to_drop, axis=1, inplace=True)
	def rename_x(df):
		for col in df:
			if col.endswith('_x'):
				df.rename(columns={col:col.rstrip('_x')}, inplace=True)
	conn= psycopg2.connect(host="localhost",dbname="odk_db", user="odk_unit", password="test")
	cur= conn.cursor()
	cur.execute("SELECT \"RESPONDENT_NAME\",\"AREA\",\"CONTACT\" from odk_db.\"CONSUMER_AWARENESS_CAMPAIGN_DIPSTICK_CORE\"")
	rows= cur.fetchall()
	print(rows)
	len_total= len(rows)
	inner_list=[]
	for i in range(len_total):
		inner_list.append(list(rows[i]))
	print(inner_list)
	df=pd.DataFrame(inner_list)
	df[2]=df[2].apply(int)
	df.rename(columns={0:'Name', 1:'Address',2:'Contact'}, inplace = True)
	#print (df)
	response=requests.get('http://127.0.0.1:5001')
	values=response.text
	df2=pd.DataFrame(eval(values))
	df2.rename(columns={0:'Name', 1:'Address',2:'Contact'}, inplace = True)
	#print(df2)
	dfn = pd.merge(df, df2, on=['Name','Address','Contact'], how='left', indicator='Exist')
	dfn['Exist'] = np.where(dfn.Exist == 'both', "True <a href='http://127.0.0.1:5001/clientinfo?clientname="+df['Name']+"'>"+"Get Info</a>",False)
	#print(dfn)
	dfn2= pd.merge(dfn,df2, on=['Contact'], how='left', indicator='PhoneExist')
	dfn2['PhoneExist'] = np.where(dfn2.PhoneExist == 'both',True,False)
	drop_y(dfn2)
	rename_x(dfn2)
	#print(dfn2)
	dfn3= pd.merge(dfn2,df2, on=['Name','Contact'], how='left', indicator='PhoneNameExist')
	dfn3['PhoneNameExist'] = np.where(dfn3.PhoneNameExist == 'both',True,False)
	drop_y(dfn3)
	rename_x(dfn3)
	print(dfn3)
	dfn4= pd.merge(dfn3,df2, on=['Name','Address'], how='left', indicator='NameAddressExist')
	dfn4['NameAddressExist'] = np.where(dfn4.NameAddressExist == 'both',True,False)
	drop_y(dfn4)
	rename_x(dfn4)
	print(dfn4)
	dfn5= pd.merge(dfn4,df2, on=['Name'], how='left', indicator='NameExist')
	dfn5['NameExist'] = np.where(dfn5.NameExist == 'both',True,False)
	drop_y(dfn5)
	rename_x(dfn5)
	# #dfn['Exist'] = np.where(dfn.Exist == 'both', "True <a href='http://127.0.0.1:5001/clientinfo?clientname="+df[0]+"'>"+"goto</a>",False)
	result=[]
	for row in range(len(dfn5.axes[0])):
		if dfn5.iloc[row]['PhoneExist']==True and dfn5.iloc[row]['PhoneNameExist']!=True :
			result.append("Phone number Exists")

		elif dfn5.iloc[row]['PhoneNameExist']==True:
			result.append("Phone and Name Exist")

		elif dfn5.iloc[row]['NameAddressExist']==True:
			result.append("Name and Address Exist")

		elif (dfn5.loc[row]['NameExist']==True and dfn5.loc[row]['NameAddressExist']==False and dfn5.loc[row]['Exist']==False):
			if dfn5.loc[row]['NameExist']==True:
				name=dfn5.loc[row]['Name'].lower()
			print(name)
			result.append("Name only exists <a href='http://127.0.0.1:5001/clientinfo?clientname="+name+"'>"+"goto</a>")
			#result.append('<a href="http://127.0.0.1:5001/clientinfo?clientname='+df['Name']+'">"+"goto</a>')
		else:
			result.append("Nothing exists")
	print(result)
	dfn5["Result"]=result
	#print(dfn5)
	for row in range(len(dfn5.axes[0])):
		if (dfn5.iloc[row]['PhoneExist']==True and dfn5.iloc[row]['PhoneNameExist']==True and dfn5.iloc[row]['NameAddressExist']==True and dfn5.iloc[row]['NameExist']==True):
			dfn5.set_value(row, 'Result',"All Exist")
	dfn5.drop(['PhoneExist','PhoneNameExist','NameAddressExist','NameExist'],axis=1, inplace=True)
	#print(dfn5)
	dfn5=dfn5.values.tolist()
	return render_template('mapping.html', chckdata=json.dumps(dfn5))


if __name__ == '__main__':
	app.run(debug=True)