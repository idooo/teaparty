
import src as library
from flask import Flask, render_template, jsonify

app = Flask(
	__name__,
	static_folder='../app',
	static_url_path='',
	template_folder='../app'
)

response = library.ResponseMocker()

@app.route("/")
def main():
	return render_template('index.html')

@app.route("/get_instances")
def get_instances():
	return jsonify(response.getInstances())

@app.route("/get_alarms")
def get_alarms():
	return jsonify(response.getAlarms())

@app.route("/get_elb")
def get_elb():
	return jsonify(response.getELB())


if __name__ == "__main__":
	app.run(debug=True)
