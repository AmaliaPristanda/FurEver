from flask import Flask, render_template, request, redirect
import cx_Oracle
import string

cx_Oracle.init_oracle_client(lib_dir=r"C:\oracle\instantclient_21_3")
dsn = cx_Oracle.makedsn("bd-dc.cs.tuiasi.ro", 1539, service_name="orcl")
con = cx_Oracle.connect(
	user="bd045",
	password="aqwre5kt",
	dsn=dsn
)
app = Flask(__name__)


######################################################## ANIMALE ##############################################

def formatDate(s: string):
	if s != 'None':
		sir = str(s).split()
		aux = sir[0]
		aux = aux.split('-')

		year = aux[0]
		day = aux[2]
		month = ' '
		if aux[1] == '01':
			month = 'JAN'
		if aux[1] == '02':
			month = 'FEB'
		if aux[1] == '03':
			month = 'MAR'
		if aux[1] == '04':
			month = 'APR'
		if aux[1] == '05':
			month = 'MAY'
		if aux[1] == '06':
			month = 'JUN'
		if aux[1] == '07':
			month = 'JUL'
		if aux[1] == '08':
			month = 'AUG'
		if aux[1] == '09':
			month = 'SEP'
		if aux[1] == '10':
			month = 'OCT'
		if aux[1] == '11':
			month = 'NOV'
		if aux[1] == '12':
			month = 'DEC'
		date = day+'-'+month+'-'+year
		return date
	return 'None'


@app.route('/')
@app.route('/animal')
def animale():
	anim = []

	cur = con.cursor()
	cur.execute('select * from animale')
	for result in cur:
		dict = {}
		dict['id_animal'] = result[0]
		dict['data_nasterii'] = formatDate(str(result[1]))
		dict['data_aducerii'] = formatDate(str(result[2]))
		dict['data_adoptiei'] = formatDate(str(result[3]))
		dict['id_tip'] = result[4]
		dict['cnp'] = result[5]
		dict['id_cusca'] = result[6]

		anim.append(dict)
	cur.close()
	return render_template('animal.html',animale=anim)


@app.route('/addAnimal', methods=['GET', 'POST'])
def add_animal():

	if request.method == 'POST':
		#pentru id_tip
		tip_name = {}
		name = "'" + request.form['denumire_tip'] + "'"

		cur = con.cursor()
		cur.execute('select id_tip from tipuri_animale where denumire_tip='+name)
		for result in cur:
			tip_name['id_tip'] = result[0]
		cur.close()

		cur = con.cursor()
		values = []

		values.append("'" + request.form['data_nasterii'] + "'")
		values.append("'" + request.form['data_aducerii'] + "'")
		values.append("'" + request.form['data_adoptiei'] + "'")

		values.append("'" + str(tip_name['id_tip']) + "'")

		values.append("'" + request.form['id_cusca'] + "'")

		fields = ['data_nasterii','data_aducerii', 'data_adoptiei', 'id_tip', 'id_cusca']
		try:
			query = 'INSERT INTO %s (%s) VALUES (%s)' % ('animale', ', '.join(fields), ', '.join(values))

			cur.execute(query)
			cur.execute('commit')
			cur.close()
		except:
			print('Eroare')
		return redirect('/animal')
	else:
		tipuri_animale = []
		cur = con.cursor()
		cur.execute('select denumire_tip from tipuri_animale')
		for result in cur:
			tipuri_animale.append(result[0])
		cur.close()

		cnpNume = []
		cur = con.cursor()
		cur.execute('select nume from client')
		for result in cur:
			cnpNume.append(result[0])
		cur.close()

		custi = []
		cur = con.cursor()
		cur.execute('select id_cusca from cusca')
		for result in cur:
			custi.append(result[0])
		cur.close()


		return render_template('addAnimal.html', cusca=custi, numeClienti=cnpNume, tipuri_animale=tipuri_animale)


@app.route('/editAnimal', methods=['POST'])
def edit_animal():

	data_nasterii = "'"+request.form['data_nasterii']+"'"
	data_aducerii = "'"+request.form['data_aducerii']+"'"
	data_adoptiei = "'"+request.form['data_adoptiei']+"'"

	cnp="'"+request.form['cnpClient']+"'"

	id_cusca = request.form['id_cusca']

	animal = ''

	try:
		cur = con.cursor()
		cur.execute('select id_animal from animale where data_nasterii =%s and data_aducerii=%s '%(str(data_nasterii), str(data_aducerii)))
		for result in cur:
			animal = result[0]
		cur.close()

		cur = con.cursor()

		q1 = "select id_cusca from animale where id_animal = %s " % (animal)

		cur.execute(q1)
		cuscaVeche = ''
		for result in cur:
			cuscaVeche = result[0]

		if str(cuscaVeche) == str(id_cusca):
			query = "update animale set data_adoptiei=%s, cnp=%s where id_animal=%s" % (data_adoptiei, cnp, animal)
		else:
			query = "update animale set id_cusca=%s where id_animal=%s" % (id_cusca, animal)
		cur.execute(query)
		cur.close()
	except:
		print('Eroare!')

	return redirect('/animal')


@app.route('/getAnimal', methods=['POST'])
def get_animal():
	anl = request.form['id_animal']

	cur = con.cursor()
	cur.execute('select * from animale where id_animal=' + anl)

	animal = cur.fetchone()

	data_nasterii = formatDate(str(animal[1]))
	data_aducerii = formatDate(str(animal[2]))
	data_adoptiei = formatDate(str(animal[3]))
	id_tip = animal[4]
	cnp = animal[5]
	id_cusca = animal[6]

	cur.close()

	custi = []
	cur = con.cursor()
	cur.execute('select id_cusca from cusca')
	for result in cur:
		custi.append(result[0])
	cur.close()

	clienti = []
	cur = con.cursor()
	cur.execute('select cnp from client')
	for result in cur:
		clienti.append(result[0])
	cur.close()

	print(clienti)
	return render_template('editAnimal.html',data_nasterii=data_nasterii, data_aducerii=data_aducerii, data_adoptiei=data_adoptiei, id_cusca=id_cusca, cusca=custi, cnp_client=cnp, cnpClienti=clienti)


@app.route('/undo',methods=['POST'])
def undoChange():
	if request.method == 'POST':
		cur = con.cursor()
		cur.execute('rollback')
		cur.execute('commit')
		return redirect('/animal')


@app.route('/permanent',methods=['POST'])
def applyChange():
	if request.method == 'POST':
		cur = con.cursor()
		cur.execute('commit')
		return redirect('/animal')

######################################################## TIPURI ANIMALE ##############################################


@app.route('/tipuri_animale')
def tipuriAnimale():
	tipuri = []

	cur = con.cursor()
	cur.execute('select * from tipuri_animale')
	for result in cur:
		tip = {}
		tip['id_tip'] = result[0]
		tip['denumire_tip'] = result[1]

		tipuri.append(tip)
	cur.close()
	return render_template('tipuri_animale.html',tipuri=tipuri)

@app.route('/addTip', methods=['GET','POST'])
def ad_tip():
	if request.method == 'POST':
		cur = con.cursor()
		values = []
		values.append("'"+request.form['denumire_tip']+"'")
		fields = ['denumire_tip']
		try:
			query='INSERT INTO %s(%s) VALUES (%s)' % (
				'tipuri_animale',
				', '.join(fields),
				', '.join(values)
			)
			cur.execute(query)
			cur.execute('commit')
		except cx_Oracle.IntegrityError:
			print('Tipul exista deja')
		return redirect('/tipuri_animale')


@app.route('/delTip', methods=['POST'])
def del_tip():
	tip = request.form['id_tip']

	try:
		cur = con.cursor()
		cur.execute('delete from tipuri_animale where id_tip=' + tip)
		cur.execute('commit')
	except:
		print('Nu se poate efectua stergerea deoarece inca exista animale de acest tip!')
	return redirect('/tipuri_animale')

######################################################## CUSCA ##############################################


@app.route('/Cusca')
def cusca():
	custi = []

	cur = con.cursor()
	cur.execute('select * from cusca order by id_cusca')
	for result in cur:
		cus = {}
		cus['id_cusca'] = result[0]
		cus['dimensiuni'] = result[1]
		cus['stare'] = result[2]

		custi.append(cus)
	cur.close()
	return render_template('Cusca.html', custi=custi)

@app.route('/addCusca', methods=['GET','POST'])
def ad_cusca():
	if request.method == 'POST':
		cur = con.cursor()
		values = []
		values.append("'"+request.form['dimensiuni']+"'")
		fields = ['dimensiuni']

		query='INSERT INTO %s(%s) VALUES (%s)' % (
			'cusca',
			', '.join(fields),
			', '.join(values)
		)
		cur.execute(query)
		cur.execute('commit')

		return redirect('/Cusca')



@app.route('/delCusca', methods=['POST'])
def del_cusca():
	tip = request.form['id_cusca']
	cur = con.cursor()
	try:
		cur.execute('delete from cusca where id_cusca =' + tip)
		cur.execute('commit')
	except:
		print('Cusca este ocupata!')
	return redirect('/Cusca')

######################################################## CLIENT ##############################################

@app.route('/client')
def client():
	clienti = []

	cur = con.cursor()
	cur.execute('select * from client')
	for result in cur:
		cl = {}
		cl['cnp'] = result[0]
		cl['nume'] = result[1]
		cl['adresa'] = result[2]

		clienti.append(cl)
	cur.close()
	return render_template('client.html', clienti=clienti)


@app.route('/addClient', methods=['GET', 'POST'])
def ad_client():
	if request.method == 'POST':
		cur = con.cursor()
		values = []
		values.append("'"+request.form['cnp']+"'")
		values.append("'"+request.form['nume']+"'")
		values.append("'"+request.form['adresa']+"'")
		fields = ['cnp', 'nume', 'adresa']
		try:
			query = 'INSERT INTO %s(%s) VALUES (%s)' % (
				'client',
				', '.join(fields),
				', '.join(values)
			)
			cur.execute(query)
			cur.execute('commit')
		except:
			print('Eroare! Verificati datele inserate!')

		return redirect('/client')

######################################################## FISA MEDICALA ##############################################

@app.route('/fisaMedicala')
def fisaMedicala():
	fise = []

	cur = con.cursor()
	cur.execute('select * from fisa_medicala order by id_animal, data desc')
	for result in cur:
		fisa = {}
		fisa['id_fisa_medicala'] = result[0]
		fisa['id_animal'] = result[1]
		fisa['data'] = formatDate(str(result[2]))
		fisa['stare_sanatate'] = result[3]
		fisa['boala'] = result[4]
		fisa['tratament'] = result[5]

		fise.append(fisa)
	cur.close()


	cur = con.cursor()
	cur.execute('select id_animal from animale')

	animale = []

	for result in cur:
		animale.append(result[0])
	cur.close()

	return render_template('fisaMedicala.html', fiseMed=fise, animale=animale)


@app.route('/addFisaMedicala', methods=['GET', 'POST'])
def ad_fisaMedicala():
	if request.method == 'POST':
		cur=con.cursor()
		values = []
		values.append("'"+request.form['id_animal']+"'")
		values.append("'"+request.form['data']+"'")
		values.append("'"+request.form['stare_sanatate']+"'")
		values.append("'"+request.form['boala']+"'")
		values.append("'"+request.form['tratament']+"'")

		fields = ['id_animal', 'data', 'stare_sanatate', 'boala', 'tratament']
		query = 'INSERT INTO %s(%s) VALUES (%s)' % (
			'fisa_medicala',
			', '.join(fields),
			', '.join(values)
		)
		cur.execute(query)
		cur.execute('commit')
		return redirect('/fisaMedicala')
	else:
		animale = []
		cur = con.cursor()
		cur.execute('select id_animal from animale')
		for result in cur:
			animale.append(result[0])
		cur.close()
		return render_template('addFisaMedicala.html', animale=animale)

@app.route('/delFisaMedicala', methods=['POST'])
def del_fisaMedicala():
	tip = request.form['id_fisa_medicala']
	cur = con.cursor()
	cur.execute('delete from fisa_medicala where id_fisa_medicala=' + tip)
	cur.execute('commit')
	return redirect('/fisaMedicala')

######################################################## DETALII ANIMALE ##############################################

@app.route('/detaliiAnimale')
def detaliiAnimale():

	detalii = []

	cur = con.cursor()
	cur.execute('select * from detalii_animale')
	for result in cur:
		det = {}
		det['id_animal'] = result[0]
		det['sex'] = result[1]
		det['nume'] = result[2]
		det['talie'] = result[3]
		det['culoare'] = result[4]
		det['rasa'] = result[5]

		detalii.append(det)
	cur.close()

	cur = con.cursor()
	cur.execute('select id_animal from animale')

	animale = []

	for result in cur:
		animale.append(result[0])
	cur.close()

	return render_template('detaliiAnimale.html', animale=animale, detalii=detalii)


@app.route('/addDetaliiAnimal', methods=['GET', 'POST'])
def ad_detaliiAnimal():

	if request.method == 'POST':
		cur = con.cursor()
		values = []
		values.append("'"+request.form['id_animal']+"'")
		values.append("'"+request.form['sex']+"'")
		values.append("'"+request.form['nume']+"'")
		values.append("'"+request.form['talie']+"'")
		values.append("'"+request.form['culoare']+"'")
		values.append("'"+request.form['rasa']+"'")
		try:
			fields = ['id_animal', 'sex', 'nume', 'talie', 'culoare', 'rasa']
			query = 'INSERT INTO %s(%s) VALUES (%s)' % (
				'detalii_animale',
				', '.join(fields),
				', '.join(values)
			)
			cur.execute(query)
			cur.execute('commit')
		except cx_Oracle.IntegrityError:
			print('Ati adaugat deja detalii pentru acest animal!')
		return redirect('/detaliiAnimale')


if __name__ == '__main__':
	app.run(debug=True)
	con.close()
