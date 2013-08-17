from flask import Flask, render_template
app = Flask(
	__name__,
	static_folder='../app',
	static_url_path='',
	template_folder='../app'
)

@app.route("/")
def main():
	return render_template('index.html')

if __name__ == "__main__":
	app.run()