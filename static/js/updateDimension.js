// Function to update CSS styles
function updateStyles(targetWidth, targetHeight) {
    const mainContainer = document.getElementById('main-container');
    mainContainer.style.width = targetWidth + 'px';
    mainContainer.style.height = targetHeight + 'px';
}

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
            updateStyles(data.target_width, data.target_height);
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
                updateStyles(data.target_width, data.target_height);
            }
        } else {
            alert('Error uploading file');
        }
    };

    uploadStartTime = new Date();
    xhr.send(formData);
});