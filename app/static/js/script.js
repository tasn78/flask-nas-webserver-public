// app/static/js/script.js
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // File selection functionality
    const fileCheckboxes = document.querySelectorAll('.file-checkbox');
    const selectAllCheckbox = document.getElementById('select-all');
    const selectedActionsDiv = document.getElementById('selected-actions');

    if (selectAllCheckbox) {
        selectAllCheckbox.addEventListener('change', function() {
            const isChecked = this.checked;
            fileCheckboxes.forEach(checkbox => {
                checkbox.checked = isChecked;
            });
            updateSelectedActions();
        });
    }

    if (fileCheckboxes.length > 0) {
        fileCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateSelectedActions);
        });
    }

    function updateSelectedActions() {
        if (!selectedActionsDiv) return;

        const selectedCount = document.querySelectorAll('.file-checkbox:checked').length;
        if (selectedCount > 0) {
            selectedActionsDiv.classList.remove('d-none');
            document.getElementById('selected-count').textContent = selectedCount;
        } else {
            selectedActionsDiv.classList.add('d-none');
        }
    }

    // Handle file upload progress
    const uploadForm = document.getElementById('upload-form');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressContainer = document.getElementById('upload-progress');

    if (uploadForm && progressBar) {
        uploadForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('file');
            if (fileInput.files.length > 0) {
                e.preventDefault();

                // Show progress bar
                progressContainer.classList.remove('d-none');
                progressBar.style.width = '0%';
                progressBar.setAttribute('aria-valuenow', 0);
                progressBar.textContent = '0%';

                // Create FormData
                const formData = new FormData(uploadForm);

                // Send upload request
                const xhr = new XMLHttpRequest();
                xhr.open('POST', uploadForm.action, true);

                // Track upload progress
                xhr.upload.addEventListener('progress', function(event) {
                    if (event.lengthComputable) {
                        const percentComplete = Math.round((event.loaded / event.total) * 100);
                        progressBar.style.width = percentComplete + '%';
                        progressBar.setAttribute('aria-valuenow', percentComplete);
                        progressBar.textContent = percentComplete + '%';
                    }
                });

                // Handle upload completion
                xhr.addEventListener('load', function() {
                    if (xhr.status === 200) {
                        window.location.reload();
                    } else {
                        alert('Upload failed. Please try again.');
                        progressContainer.classList.add('d-none');
                    }
                });

                xhr.send(formData);
            }
        });
    }
});