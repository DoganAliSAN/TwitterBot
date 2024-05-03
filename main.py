import tweepy
import openai
from flask import Flask, render_template, request, redirect, url_for
from support import Support

app = Flask(__name__, static_folder='templates/static')
support = Support("keys.ini")

bearer_token = support.read_config("KEYS", "bearer_token")
consumer_key = support.read_config("KEYS", "consumer_key")
consumer_secret = support.read_config("KEYS", "consumer_secret")
access_token = support.read_config("KEYS", "access_token")
access_token_secret = support.read_config("KEYS", "access_token_secret")

client = tweepy.Client(bearer_token, consumer_key, consumer_secret, access_token, access_token_secret)
auth = tweepy.OAuth1UserHandler(consumer_key, consumer_secret, access_token, access_token_secret)
api = tweepy.API(auth)

app.secret_key = 'MySeCrEtK3Y'  # Set a secret key for the Flask app

image_url = ""  

@app.route('/', methods=['GET', 'POST'])
def hello():
    global image_url
    if request.method == 'POST':
        if "submitButton" in request.form:
            form_data = request.form
            openai.api_key = support.read_config("KEYS", "openai_key")
            response = openai.Image.create(prompt=str(form_data["inputValue"]), n=2, size="1024x1024")["data"][0]["url"]
            image_url = response
            return redirect(url_for('result'))  # Redirect to the 'result' endpoint
        else:
            response = request.form
            print(response)

    return render_template('index.html')

@app.route('/result', methods=['GET','POST'])
def result():
    data = request.args.get('data')

    return render_template('result.html', data=image_url)

@app.route('/tweet', methods=['POST'])
def tweet():
    global image_url
    if image_url != "":
        print(image_url)
        tweet_text = "Making a Bot for my improvement"
        support.download_image(image_url, "images/" + image_url.split("/")[-1])
        media_path = "images/" + image_url.split("/")[-1]
        media = api.media_upload(filename=media_path)
        client.create_tweet(text=tweet_text, media_ids=[media.media_id])
        image_url = ""
    else:
        print("Something wrong with the image URL")
    return redirect(url_for('hello'))


@app.route('/keys',methods=['GET','POST'])
def keys():
    """ if request.method == 'POST'
        new_openai_key = request.form.get('openai_key')
        support.write_config("KEYS", "openai_key", new_openai_key)
     """    
    dict = {"openai_key":support.read_config("KEYS","openai_key"), "bearer_token":bearer_token, "consumer_key":consumer_key, "consumer_secret":consumer_secret, "access_token":access_token, "access_token_secret":access_token_secret}
    openai_key = support.read_config("KEYS","openai_key")
    return render_template('keys.html', data=dict)

@app.route('/update_keys', methods=['POST'])
def update_keys():
    if request.method == 'POST':
        # Get the new key values from the submitted form
        new_openai_key = request.form.get('openai_key')
        new_bearer_token = request.form.get('bearer_token')
        new_consumer_key = request.form.get('consumer_key')
        new_consumer_secret = request.form.get('consumer_secret')
        new_access_token = request.form.get('access_token')
        new_access_token_secret = request.form.get('access_token_secret')

        # Update the key values in the configuration file
        support.write_config("KEYS", "openai_key", new_openai_key)
        support.write_config("KEYS", "bearer_token", new_bearer_token)
        support.write_config("KEYS", "consumer_key", new_consumer_key)
        support.write_config("KEYS", "consumer_secret", new_consumer_secret)
        support.write_config("KEYS", "access_token", new_access_token)
        support.write_config("KEYS", "access_token_secret", new_access_token_secret)

        # Redirect back to the keys page to display the updated values
        return redirect(url_for('keys'))

    return render_template('keys.html', data=dict)

if __name__ == '__main__':
    app.run(debug=True)