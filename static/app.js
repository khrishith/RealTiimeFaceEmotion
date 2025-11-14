let running = false;
let currentFilter = 'none';

const toggleBtn = document.getElementById('toggle-btn');
const videoFeed = document.getElementById('video-feed');
const filterButtons = document.querySelectorAll('.filter-btn');

toggleBtn.addEventListener('click', () => {
    fetch('/toggle_stream', { method: 'POST' })
    .then(res => res.json())
    .then(data => {
        running = data.running;
        toggleBtn.innerText = running ? 'Stop Camera' : 'Start Camera';
        if (running) updateVideo();
    });
});

filterButtons.forEach(btn => {
    btn.addEventListener('click', () => {
        currentFilter = btn.getAttribute('data-filter');
        filterButtons.forEach(b => b.style.border = 'none');
        btn.style.border = '2px solid #00ff99';
    });
});

function updateVideo() {
    if (!running) return;

    videoFeed.src = '/video_feed';
    videoFeed.onload = () => {
        applyFilter();
    };

    // Update chart every 1s
    updateEmotionChart();
    setTimeout(updateVideo, 200);
}

function applyFilter() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    canvas.width = videoFeed.width;
    canvas.height = videoFeed.height;
    ctx.drawImage(videoFeed, 0, 0, canvas.width, canvas.height);
    let imageData = ctx.getImageData(0,0,canvas.width,canvas.height);
    let data = imageData.data;

    switch(currentFilter) {
        case 'sketch':
            for (let i=0;i<data.length;i+=4){
                let avg = (data[i]+data[i+1]+data[i+2])/3;
                data[i] = data[i+1] = data[i+2] = 255 - avg;
            }
            break;
        case 'cartoon':
            for (let i=0;i<data.length;i+=4){
                data[i] = Math.floor(data[i]/32)*32;
                data[i+1] = Math.floor(data[i+1]/32)*32;
                data[i+2] = Math.floor(data[i+2]/32)*32;
            }
            break;
        case 'oil':
            for (let i=0;i<data.length;i+=4){
                data[i] = data[i] + 20;
                data[i+1] = data[i+1] + 10;
                data[i+2] = data[i+2];
            }
            break;
        case 'emboss':
            for (let i=0;i<data.length;i+=4){
                data[i] = 128 + data[i] - data[i+1];
                data[i+1] = 128 + data[i+1] - data[i+2];
                data[i+2] = 128 + data[i+2] - data[i];
            }
            break;
        case 'sepia':
            for (let i=0;i<data.length;i+=4){
                let r = data[i], g = data[i+1], b = data[i+2];
                data[i] = (r*0.393 + g*0.769 + b*0.189);
                data[i+1] = (r*0.349 + g*0.686 + b*0.168);
                data[i+2] = (r*0.272 + g*0.534 + b*0.131);
            }
            break;
    }

    ctx.putImageData(imageData,0,0);
    videoFeed.src = canvas.toDataURL();
}

let ctx = document.getElementById('emotionChart').getContext('2d');
let emotionChart = new Chart(ctx, {
    type: 'bar',
    data: {
        labels: ['angry','disgust','fear','happy','neutral','sad','surprise'],
        datasets: [{
            label: 'Emotions Count',
            data: [0,0,0,0,0,0,0],
            backgroundColor: '#00aaff'
        }]
    },
    options: { responsive: true, animation: { duration: 0 }, scales: { y: { beginAtZero: true } } }
});

function updateEmotionChart(){
    fetch('/get_emotion_history')
    .then(res => res.json())
    .then(data => {
        emotionChart.data.datasets[0].data = Object.values(data);
        emotionChart.update();
    });
}
