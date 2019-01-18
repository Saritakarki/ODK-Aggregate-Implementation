from flask import Flask, render_template,jsonify, request
import psycopg2
import json
import requests


app= Flask(__name__)
app.config["DEBUG"] = True
@app.route('/', methods=['GET'])
def client():
	conn= psycopg2.connect(host="localhost",dbname="client", user="odk_unit", password="test")
	cur= conn.cursor()
	cur.execute("SELECT cname,carea,ccontact from client.user")
	rows=cur.fetchall()
	#print(rows)
	#print(rows[0])
	len_total= len(rows)
	inner_list=[]
	for i in range(len_total):
		inner_list.append(list(rows[i]))
	#print(inner_list)
	# cname_list=['cname','carea','ccontact']
	# finaldict={'column':cname_list, 'data': inner_list}
	return ( json.dumps(inner_list))
@app.route('/clientinfo', methods=['GET'])
def clientinfo():
	cname=request.args.get('clientname')
	print(cname)
	print("jkjk")
	conn= psycopg2.connect(host="localhost",dbname="client", user="odk_unit", password="test")
	cur= conn.cursor()
	print("SELECT * from client.user where lower(cname)=lower('"+(cname)+"')")
	cur.execute("SELECT * from client.user where lower(cname)=lower('"+(cname)+"')")
	rows=cur.fetchall()
	print(rows)
	len_total= len(rows)
	inner_list=[]
	for i in range(len_total):
		inner_list.append(list(rows[i]))
	print(inner_list)
	return (jsonify(inner_list))

if __name__=='__main__':
	app.run(host="127.0.0.1",port=5001,debug=True)


