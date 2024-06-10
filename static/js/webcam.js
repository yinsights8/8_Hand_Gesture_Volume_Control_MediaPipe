let isWebcamOn = false;
let uploadStartTime;

document.getElementById('start-webcam').addEventListener('click', function() {
    isWebcamOn = true;
    fetch('/toggle_webcam', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ iswebcam: isWebcamOn })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'webcam_on') {
            document.getElementById('video-container').style.display = 'block';
            document.getElementById('video-stream').src = "{{ url_for('video_feed') }}";
            document.getElementById('start-webcam').style.display = 'none';
            document.getElementById('stop-webcam').style.display = 'inline';
        }
    });
});

document.getElementById('stop-webcam').addEventListener('click', function() {
    isWebcamOn = false;
    fetch('/toggle_webcam', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ iswebcam: isWebcamOn })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'webcam_off') {
            document.getElementById('video-container').style.display = 'none';
            document.getElementById('video-stream').src = '';
            document.getElementById('start-webcam').style.display = 'inline';
            document.getElementById('stop-webcam').style.display = 'none';
            document.getElementById('play-streaming').style.display = 'none';
            document.getElementById('stop-streaming').style.display = 'none';
        }
    });
});

document.getElementById('upload-file').addEventListener('click', function() {
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];
    if (!file) {
        alert('No file selected');
        return;
    }

    const formData = new FormData();
    formData.append('uploadedFile', file);

    const xhr = new XMLHttpRequest();
    xhr.open('POST', '/upload_file', true);

    xhr.upload.onprogress = function(event) {
        if (event.lengthComputable) {
            const percentComplete = (event.loaded / event.total) * 100;
            const timeElapsed = ((new Date()) - uploadStartTime) / 1000;
            document.getElementById('loading-bar').style.display = 'block';
            document.querySelector('#loading-bar .bar').style.width = percentComplete + '%';
            document.querySelector('#loading-bar .time').textContent = timeElapsed.toFixed(1) + 's';
        }
    };

    xhr.onload = function() {
        if (xhr.status === 200) {
            const data = JSON.parse(xhr.responseText);
            if (data.status === 'file_uploaded') {
                document.getElementById('loading-bar').style.display = 'none';
                document.getElementById('video-container').style.display = 'block';
                document.getElementById('video-stream').src = "{{ url_for('video_feed') }}";
                document.getElementById('start-webcam').style.display = 'inline';
                document.getElementById('stop-webcam').style.display = 'none';
                document.getElementById('play-streaming').style.display = 'inline';
                document.getElementById('stop-streaming').style.display = 'inline';
                askToPlayStreaming();
            }
        } else {
            alert('Error uploading file');
        }
    };

    uploadStartTime = new Date();
    xhr.send(formData);
});

document.getElementById('play-streaming').addEventListener('click', function() {
    document.getElementById('video-stream').src = "{{ url_for('video_feed') }}";
    document.getElementById('play-streaming').style.display = 'none';
    document.getElementById('stop-streaming').style.display = 'inline';
});

document.getElementById('stop-streaming').addEventListener('click', function() {
    document.getElementById('video-stream').src = '';
    document.getElementById('play-streaming').style.display = 'inline';
    document.getElementById('stop-streaming').style.display = 'none';
});

window.addEventListener('beforeunload', function() {
    fetch('/toggle_webcam', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ iswebcam: false })
    });
});

function askToPlayStreaming() {
    if (confirm('Do you want to start streaming the uploaded video?')) {
        document.getElementById('play-streaming').click();
    }
}