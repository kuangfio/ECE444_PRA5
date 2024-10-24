import pytest
from pathlib import Path
import pytest_benchmark
from application import application, load_model, load_vectorizer, predict
import re
from urllib.parse import urlencode
from urllib.request import urlopen

#load model locally
model = load_model()
vectorizer = load_vectorizer()

@pytest.fixture
def client():
    application.config["TESTING"] = True

    with application.app_context():
        
        yield application.test_client()  # tests run here

def test_model(client):
    headlines = ["This+is+fake+news", "This+is+real+news", "BREAKING+NEWS", "Local+library+event"]
    correct_predictions = ["\"This is fake news\" is FAKE news.", 
                           "\"This is real news\" is REAL news.",
                           "\"BREAKING NEWS\" is FAKE news.",
                           "\"Local library event\" is REAL news."]
    
    predictions = get_predictions(client, headlines)

    assert correct_predictions == predictions

def get_predictions(client, headlines):
    
    predictions= []
    for headline in headlines:
        page = client.get("?query="+headline, follow_redirects=True)
        #print(page.text)
        prediction = re.search("<h2 id=\"pred\">(?P<pred>.*)</h2>", page.text)
        if prediction != None:
            predictions.append(prediction.group("pred"))
        else:
            predictions.append(prediction)
    return predictions

def call_server(query_string):
    server="test-serve-sent-env-2.eba-gv6kmnuj.us-east-1.elasticbeanstalk.com"
    url = f"http://{server}/?query={query_string}"
    with urlopen(url) as response:
        page_result = response.read()
        prediction = re.search("<h2 id=\"pred\">(?P<pred>.*)</h2>", str(page_result))
    
    return prediction
    

def test_single_latency(benchmark):
    result = benchmark(call_server,"This+is+fake+news")

    assert result != None

def test_many_latency_fake(benchmark):
    benchmark.pedantic(call_server, args=["This+is+fake+news"], rounds=100, iterations=1)

    assert 1

def test_many_latency_true(benchmark):
    benchmark.pedantic(call_server, args=["This+is+real+news"], rounds=100, iterations=1)

    assert 1

def test_many_latency_fake_two(benchmark):
    benchmark.pedantic(call_server, args=["BREAKING+NEWS"], rounds=100, iterations=1)

    assert 1

def test_many_latency_true_two(benchmark):
    benchmark.pedantic(call_server, args=["Local+library+event"], rounds=100, iterations=1)

    assert 1

def test_local_latency(benchmark, client):
    result = benchmark(get_predictions, client, ["This is real news"])
    assert result == ['"This is real news" is REAL news.']

def test_many_local_latency(benchmark, client):
    
    benchmark.pedantic(get_predictions, args=[client, ["This is real news"]], rounds=100, iterations=1)

    assert 1

def local_prediction():
    query_string = "This is real news"
    return predict(model, vectorizer, query_string)