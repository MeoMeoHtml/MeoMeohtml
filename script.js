// Tải TLTOOL.py
async function downloadTLTOOL() {
  const url = 'https://raw.githubusercontent.com/hocdaobitcoin-del/TLTOOL.py/refs/heads/main/TLTOOL.py';
  // Tìm nút được click (hỗ trợ cả .btn-tool và .btn-small)
  const button = event.target.closest('.btn-tool, .btn-small');
  if (!button) return;
  const originalText = button.innerHTML;
  button.innerHTML = '<i class="fas fa-spinner fa-pulse"></i> Đang tải...';
  button.disabled = true;

  try {
    const response = await fetch(url);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const blob = await response.blob();
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = blobUrl;
    a.download = 'TLTOOL.py';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(blobUrl);
  } catch (error) {
    alert('Có lỗi khi tải file: ' + error.message);
  } finally {
    button.innerHTML = originalText;
    button.disabled = false;
  }
}

// Hiển thị/ẩn modal
function showModal(id) {
  document.getElementById(id).classList.add('active');
}

function hideModal(id) {
  document.getElementById(id).classList.remove('active');
}

// Xử lý form liên hệ (demo)
function handleContact(e) {
  e.preventDefault();
  alert('Cảm ơn ní! Tin nhắn đã được gửi (demo).');
  hideModal('contactModal');
}

// Đóng modal khi click ra ngoài
window.onclick = function(e) {
  if (e.target.classList.contains('modal-overlay')) {
    e.target.classList.remove('active');
  }
};