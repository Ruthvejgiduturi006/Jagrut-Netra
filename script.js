function openSection(section) {
    let contentDiv = document.getElementById('content');
    contentDiv.innerHTML = '';

    if (section === 'crowd') {
        contentDiv.innerHTML = `
            <h2>Crowd Management</h2>
            <p>Live counting of people in a crowded area.</p>
            <button onclick="detectFaces()">Start Counting</button>
        `;
    } else if (section === 'missing_persons') {
        contentDiv.innerHTML = `
            <h2>Missing Persons</h2>
            <input type="file" id="uploadFile">
            <button onclick="uploadImage()">Upload Image</button>
        `;
    } else if (section === 'restricted_area') {
        contentDiv.innerHTML = `
            <h2>Restricted Area Security</h2>
            <p>Detects unauthorized individuals in restricted areas.</p>
        `;
    } else if (section === 'night_security') {
        contentDiv.innerHTML = `
            <h2>Night Security Monitoring</h2>
            <p>Real-time monitoring for public safety at night.</p>
        `;
    }
}

function uploadImage() {
    let fileInput = document.getElementById('uploadFile').files[0];
    let formData = new FormData();
    formData.append('file', fileInput);

    fetch('http://127.0.0.1:5000/upload', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => alert(data.message));
}

function detectFaces() {
    fetch('http://127.0.0.1:5000/detect_faces', {
        method: 'POST'
    }).then(response => response.json())
      .then(data => {
          console.log(data);
          alert("Face data detected! Check the console for details.");
      });
}
