# Concurrency is a problem, and there will be a 502 error if two requests come in at the same time.

from flask import Flask, request, render_template, flash, redirect, Response
from werkzeug.utils import secure_filename
from flask import jsonify
import os, time
import random
import json

from HelperFunctions import splitter, clear_temp, allowed_file
from ModelFunctions import main as img_detector

app = Flask(__name__, template_folder='templates')

# Multiple users will conflict. Transition to a generator/temporary memory solution.
if not os.path.isdir('TEMPPICS'):
    os.mkdir('TEMPPICS')
if not os.path.isdir('TEMPVID'):
    os.mkdir('TEMPVID')


@app.route('/')
def home():
    return render_template("index.html")


@app.route('/test_api', methods=['POST'])
def test_api():
    video = request.files['video']
    random_bit = random.getrandbits(1)
    random_boolean = bool(random_bit)
    return jsonify({'Random Test Boolean':random_boolean})


@app.route('/api', methods=['POST'])
def api():
    print("/api post request received")
    start_time = time.time()
    
    # Checks to make sure a file was actually received with the key 'video'
    if 'video' not in request.files:
        flash('No file part')
        return redirect(request.url)
    video = request.files['video']
    letter = request.form.get('expected')
    letter = letter.upper()

    # Checks to make sure the video has a filename.
    # if video.filename == '':
    #     flash('No Selected File')
    #     return redirect(request.url)

    if video: # and allowed_file(video.filename): # If a video exists and it's of an appropriate type
        print("Video Filename:", video.filename)
        filename = secure_filename(video.filename) # Apparently a good method to use to make sure no one can do silly things with filenames.
        video.save(os.path.join('TEMPVID','test_' + filename)) #Saves our video file to the TEMPVID folder.
        print(f"Did video save? {len(os.listdir('TEMPVID'))>0}")
    else:
        flash('File of incorrect type.')
        return redirect(request.url)

    splitter_start_time = time.time()
    for vid in os.listdir('TEMPVID'):
        splitter(vid, frameskip=10) #Frameskip allows us to designate that we only save frames with a count % frameskip. 1 saves every frame.
    splitter_end_time = time.time()
    print(f"Total Splitter runtime - {(splitter_end_time - splitter_start_time):.2f} seconds")

    # Actual DS magic happens here.
    classes, confidences = img_detector()
    predictions = list(zip(classes, confidences))
    clear_temp() # Helper function that clears both of the temporary folders.
    end_time = time.time()
    
    Dictionary = {
        'A': 0,
        'B': 1,
        'C': 2,
        'D': 3,
        'E': 4,
        'F': 5,
        'G': 6,
        'H': 7,
        'I': 8,
        'J': 9,
        'K': 10,
        'L': 11,
        'M': 12,
        'N': 13,
        'O': 14,
        'P': 15,
        'Q': 16,
        'R': 17,
        'S': 18,
        'T': 19,
        'U': 20,
        'V': 21,
        'W': 22,
        'X': 23,
        'Y': 24,
        'Z': 25,
    }

    testing_list = []
    print("Predictions-\n",predictions)
    for double in predictions:
        print("Double", double)
        holding_array = []
        for individual in double:
            print("Individual", individual)
            if len(individual) != 0:
                holding_array.append(float(individual[0]))
        testing_list.append(holding_array)

    testing_list.append([f"Time of operation: {(end_time-start_time):.3f} seconds"])
    print("Testing List", testing_list)



    # Check that predictions match expected
    is_match = False

    if len(testing_list[0]) != 0:
        if Dictionary[letter] == testing_list[0][0]:
            is_match = True

    if len(testing_list[0]) > 1:
        confidence = testing_list[0][1]
    else:
        confidence = 0
    testing_list[0] = (letter, is_match, confidence)


    X = json.dumps(testing_list)
    # print(Dictionary[letter])
    # print(testing_list[0][0])
    # print('COOPER VOS IS E', is_match)
    return Response(X,  mimetype='application/json')

if __name__ == '__main__':
    app.run(host="0.0.0.0")