const express = require('express')
const app = express()
const basicAuth = require('express-basic-auth')
const bodyParser = require('body-parser');
const { Pool, Client } = require('pg');

const pool = new Pool({
	user: "postgres",
	host: "localhost",
	database: "course_moniter",
	port: 5432
});

function getData(callback){
	data = {}
	pool.query("SELECT value FROM stats WHERE stat = 'last_check'", (DBerr, DBres) => {
		if (DBerr){
			console.log(DBerr.stack)
		}
		data.lastCheck = DBres.rows[0].value
		pool.query("SELECT * FROM courses", (DBerr, DBres) => {
			if (DBerr) {
				console.log(DBerr.stack)
			}
			data.courses = [];
			DBres.rows.forEach((row) => {
				data.courses.push({
					"name": row.dept + " " + row.course + " " + row.section,
					"status": row.status,
					"id": row.id
				})
			})
			callback(data)
		})
	})
}

function addCourse(dept, course, section, campus)
{
	pool.query(
		"INSERT INTO courses(dept, course, section, campus) VALUES ($1, $2, $3, $4)",
		[dept, course, section, campus],
		(DBerr, DBres) => {
			if (DBerr) {
				console.log(DBerr.stack)
			}
		}
	)
}

function removeCourse(id)
{
	pool.query(
		"DELETE FROM courses WHERE id = $1",
		[id],
		(DBerr, DBres) => {
			if(DBerr) {
				console.log(DBerr.stack)
			}
		}
	)
}

app.use(basicAuth({
	users: {'stu': 'ubc802'},
	challenge: true
}))

app.use(bodyParser.json());

app.set('views', __dirname + "/views")
app.set('view engine', 'ejs')

app.get('/', (req, res) => {
	getData((data) => {
		// data.timeSinceLastCheck = new Date(Date.now() - data.lastCheck * 1000).toISOString().substr(11, 8)
		res.render('dashboard', { data : data })
	})
})

app.post('/remove', (req, res) => {
	removeCourse(req.body.id)
	res.end()
})

app.post('/add', (req, res) => {
	addCourse(req.body.dept, req.body.course, req.body.section, req.body.campus)
	res.end()
})

exports.app = app

if (require.main === module) {
	app.listen(3000)
}