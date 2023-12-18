from flask import Flask, render_template, redirect, url_for, request, jsonify
import json
import os
import uuid
import datetime

app = Flask(__name__)

# Funtion to read from data.json file or demo purposes
def read_data():
    if not os.path.exists('data.json'):
        with open('data.json', 'w') as f:
            json.dump({}, f)
    with open('data.json', 'r') as f:
        return json.load(f)

def strp_time(time):
    return datetime.datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f')

@app.route('/')
def index():
    links = read_data()
    current_time = datetime.datetime.now()
    link_data = []
    for link_id, link_info in links.items():
        status = "Active" if current_time < strp_time(link_info['expiration']) else "Expired"
        remaining_time = strp_time(link_info['expiration']) - current_time if status == "Active" else datetime.timedelta(0)
        #  if remaining_time is days, then only send days, if hours then only send hours, if minutes then only send minutes
        if remaining_time.days > 0:
            remaining_time = f"{remaining_time.days} days"
        if remaining_time.seconds // 3600 > 0:
            remaining_time = f"{remaining_time.seconds // 3600} hours"
        if remaining_time.seconds // 60 > 0:
            remaining_time = f"{remaining_time.seconds // 60} minutes"
        link_data.append({
            'id': link_id,
            'title': link_info['title'],
            'status': status,
            'remaining_time': remaining_time,
        })

    return render_template('index.html', links=link_data)


@app.route('/create_link', methods=['POST'])
def create_link():
    links = read_data()

    title = request.form.get('title')
    duration = request.form.get('duration')
    unit = request.form.get('unit')
    images = request.files.getlist('images')

    link_id = str(uuid.uuid4())[:18]  # Generate a unique identifier

    # Calculate expiration time based on the unit
    expiration_time = datetime.datetime.now()
    if unit == "Days":
        expiration_time += datetime.timedelta(days=int(duration))
    elif unit == "Hours":
        expiration_time += datetime.timedelta(hours=int(duration))
    elif unit == "Minutes":
        expiration_time += datetime.timedelta(minutes=int(duration))

    # Create a directory for the link
    link_dir = os.path.join('static', 'images', link_id)
    os.makedirs(link_dir, exist_ok=True)

    # Save images to the directory
    for image in images:
        image.save(os.path.join(link_dir, image.filename))

    links[link_id] = {
        'expiration': str(expiration_time),
        'title': title, 
        'images': [image.filename for image in images]}

    # Write the data to the file
    with open('data.json', 'w') as f:
        json.dump(links, f)

    return jsonify({'message': f'Link created: {link_id}', 'link_id': link_id})


@app.route('/temporary/<link_id>')
def temporary(link_id):
    links = read_data()
    if link_id in links:
        if datetime.datetime.now() < strp_time(links[link_id]['expiration']):
            return render_template('link_active.html', link_id=link_id, images=links[link_id]['images'])
        else:
            return render_template('link_expired.html')
    return "Invalid link"

if __name__ == '__main__':
    app.run(debug=True, port=7227)
