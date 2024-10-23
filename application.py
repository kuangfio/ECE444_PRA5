from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from flask import (
    Flask,
    render_template,
    request,
    session
)


# create and initialize a new Flask app
application = Flask(__name__)
# load the config
application.config.from_object(__name__)

def load_model():
    #model loading
    loaded_model = None
    with open("basic_classifier.pkl", "rb") as fid:
        loaded_model = pickle.load(fid)
    return loaded_model

def load_vectorizer():
    vectorizer = None
    with open("count_vectorizer.pkl", "rb") as vd:
        vectorizer = pickle.load(vd)
    return vectorizer

def predict(loaded_model, vectorizer, string):
    #how to use model to predict
    prediction = loaded_model.predict(vectorizer.transform([string]))[0]
    return prediction

model = load_model()
vectorizer = load_vectorizer()

@application.route("/", methods=["GET"])
def index():
    headline = request.args.get("query")
    prediction = None
    if headline != None:
        prediction = predict(model, vectorizer, headline)
        return render_template("index.html", headline=headline, prediction=prediction)
    return render_template("index.html")

@application.route("/hello")
def hello():
    return "Hello World!"

if __name__ == "__main__":
    application.run(port=5000, debug=True)