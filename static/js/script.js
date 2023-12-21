function handleSubmit() {
    var button = document.getElementById('getVideosButton');
    button.disabled = true;  // 버튼 비활성화
    button.style.backgroundColor = '#cccccc'; // 버튼을 회색으로 변경
    showLoadingAnimation(); // 로딩 애니메이션 활성화
}

// 페이지 로드 시 enableButton 함수를 호출
window.onload = enableButton;

function enableButton() {
    var button = document.getElementById('getVideosButton');
    if(button) {
        button.disabled = false;  // 버튼 활성화
        button.style.backgroundColor = ''; // 스타일 초기화
    }
}

function showLoadingAnimation() {
    document.getElementById('loadingAnimation').style.display = 'block';
}

// 자막 다운로드 함수
function downloadSubtitle(channelId, videoId, button) {
    // 버튼 비활성화 및 스타일 변경
    button.disabled = true;
    button.className = 'downloading-button';
    button.innerHTML = 'Downloading...';

    // 로딩 애니메이션 요소 생성 및 추가
    var loader = document.createElement('div');
    loader.className = 'loader';
    button.parentNode.insertBefore(loader, button.nextSibling);

    fetch(`/download/${channelId}/${videoId}`)
        .then(response => {
            // 다운로드 후 처리

            // 페이지 새로고침
            window.location.reload();
        })
        .catch(error => {
            console.error('Error:', error);
            button.disabled = false;
            button.className = 'download-link';
            button.innerHTML = 'Download Subtitle';
            loader.remove();
        });
}