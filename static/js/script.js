function handleSubmit() {
    var button = document.getElementById('getVideosButton');
    button.disabled = true;  // 버튼 비활성화
    showLoadingAnimation(); // 로딩 애니메이션 활성화
}

function showLoadingAnimation() {
    document.getElementById('loadingAnimation').style.display = 'block';
}

function enableButton() {
    var button = document.getElementById('getVideosButton');
    if(button) {
        button.disabled = false;  // 버튼 활성화
    }
}

// 페이지 로드 시 enableButton 함수를 호출
window.onload = enableButton;