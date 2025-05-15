// Change profile picture preview
const uploadPicInput = document.getElementById('upload-pic');
const profilePic = document.getElementById('profile-pic');

uploadPicInput.addEventListener('change', function() {
    const file = this.files[0];
    if (file && file.type.startsWith('image/')) {
        const reader = new FileReader();
        reader.onload = function(e) {
            profilePic.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
});
