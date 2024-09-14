$(document).ready(function() {
    console.log('Script is loaded and running');
});
$(document).ready(function() {
    $('.slide').on('click', '.item', function() {
        var bgImage = $(this).css('background-image');

        var imageUrl = bgImage.match(/url\("?(.+?)"?\)/)[1];

        $.magnificPopup.open({
            items: {
                src: imageUrl
            },
            type: 'image',
            closeBtnInside: true,
            closeOnContentClick: true,
            gallery: {
                enabled: true
            },
            image: {
                verticalFit: true
            }
        });
    });
});

let next = document.querySelector('.next');
let prev = document.querySelector('.prev');
let activeItemIndex = 1; // Initialize the active item index variable
let activeItem = document.querySelector('.item:nth-child(2)'); // Initialize the active item variable

next.addEventListener('click', function() {
     const slider = document.querySelector('.slide');
    let items = document.querySelectorAll('.item');
    activeItemIndex = (activeItemIndex + 1) % items.length; // Update the active item index variable
    document.querySelector('.slide').appendChild(items[0]);
    updateActiveItem(); // Update the active item variable
});

prev.addEventListener('click', function() {
    const slider = document.querySelector('.slide');
    let items = document.querySelectorAll('.item');
    activeItemIndex = (activeItemIndex - 1 + items.length) % items.length; // Update the active item index variable
    document.querySelector('.slide').prepend(items[items.length - 1]);
    updateActiveItem(); // Update the active item variable
});

function updateActiveItem() {
    let items = document.querySelectorAll('.item');
    activeItem = items[activeItemIndex]; // Update the active item variable
}

document.getElementById('imageUpload').addEventListener('change', function() {
    const reader = new FileReader();
    reader.onload = function(e) {
        console.log('File upload event listener triggered');
        console.log('Active item:', activeItem);
        console.log('Background image URL:', `url(${e.target.result})`);
        activeItem.style.backgroundImage = `url(${e.target.result})`;
    };
    reader.readAsDataURL(this.files[0]);
});

function triggerFileInput() {
    document.getElementById('vton_img').click();
}

document.getElementById('vton_img').addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const uploadButton = document.getElementById('imageUpload');
        const uploadText = document.getElementById('upload-text');
        const uploadSuccess = document.getElementById('upload-success');

        // Trigger the animation
        uploadButton.classList.add('click');

        // Update the text (this might not be visible during the animation)
        uploadText.textContent = file.name;

        // Read and display the image
        const reader = new FileReader();
        reader.onload = function(e) {
            addImageToSlider(e.target.result, true);
        };
        reader.readAsDataURL(file);

        // Remove the 'click' class after the animation completes
        setTimeout(() => {
            uploadButton.classList.remove('click');
            uploadSuccess.style.display = 'block';
            uploadButton.classList.add('file-selected');
        }, 2500); // 2.5 seconds, matching the longest animation duration
    }
});

function buttonClicked() {
    // This function is now handled by the file input change event
}



const dropdownBtn = document.querySelector("#dropdown-btn");
const dropdown = document.querySelector("#dropdown");
const DROPDOWN_ANIMATION = {
  open: "dropdown-open",
  close: "dropdown-close"
};

let isOpen = false;

const dropdownOutsideClick = (ev) => {
  if (isOpen && !dropdown.contains(ev.target) && ev.target !== dropdownBtn) {
    isOpen = false;
    closeDropdown();
  }
};

const openDropdown = () => {
  dropdown.classList.remove("hidden", DROPDOWN_ANIMATION.close); // Ensure previous close animation and hidden class are removed
  dropdown.classList.add(DROPDOWN_ANIMATION.open); // Start open animation
  isOpen = true;
};

const closeDropdown = () => {
  dropdown.classList.remove(DROPDOWN_ANIMATION.open); // Remove open animation
  dropdown.classList.add(DROPDOWN_ANIMATION.close); // Start close animation

  dropdown.addEventListener("animationend", () => {
    if (!isOpen) {
      dropdown.classList.add("hidden"); // Hide the dropdown after close animation finishes
    }
  }, { once: true });
};

const toggleDropdown = (event) => {
  event.stopPropagation(); // Prevent click event from reaching the body
  isOpen = !isOpen;
  isOpen ? openDropdown() : closeDropdown();
};

const updateDropdownValue = (event) => {
  const selectedOption = event.target.textContent; // Get the text of the clicked button
  dropdownBtn.innerHTML = `${selectedOption}
    <svg viewBox="0 0 320 512" width="13" title="angle-down" class="ml-2 dropdown-icon">
      <path d="M143 352.3L7 216.3c-9.4-9.4-9.4-24.6 0-33.9l22.6-22.6c9.4-9.4 24.6-9.4 33.9 0l96.4 96.4 96.4-96.4c9.4-9.4 24.6-9.4 33.9 0l22.6 22.6c9.4 9.4 9.4 24.6 0 33.9l-136 136c-9.2 9.4-24.4 9.4-33.8 0z" />
    </svg>`; // Update button's innerHTML with selected option and SVG
  closeDropdown(); // Close the dropdown after selection
};

const fileInput = document.getElementById('vton_img');

fileInput.addEventListener('change', function(event) {
    const file = event.target.files[0];
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            addImageToSlider(e.target.result, true);
        };
        reader.readAsDataURL(file);
    }
});

function addImageToSlider(imageUrl, isUpload = false) {
    const slider = document.querySelector('.slide');
    const newItem = document.createElement('div');
    newItem.classList.add('item');
    newItem.style.backgroundImage = `url(${imageUrl})`;

    const content = document.createElement('div');
    content.classList.add('content');
    content.innerHTML = `
        <button class="button-send" ${isUpload ? 'disabled' : 'disabled'}>
            <span class="button-text">Change Pose</span>
            <div class="button-loader">
                <div></div>
                <div></div>
                <div></div>
            </div>
        </button>
    `;
    newItem.appendChild(content);

    // If it's the uploaded garment image, insert it as the first item
    if (isUpload) {
        if (slider.firstChild) {
            slider.replaceChild(newItem, slider.firstChild);
        } else {
            slider.appendChild(newItem);
        }
        updateActiveItemIndex(0);
    } else {
        // Insert processed images after the current active item
        const activeItem = slider.children[activeItemIndex];
        slider.insertBefore(newItem, activeItem.nextSibling);
        updateActiveItemIndex(activeItemIndex + 1);
    }

    // Limit the number of items in the slider
    if (slider.children.length >= 4) {
        slider.removeChild(slider.lastChild);
    }
}

function updateActiveItemIndex(newIndex) {
    activeItemIndex = newIndex % document.querySelectorAll('.item').length;
    updateActiveItem();
}

// Update the existing next and prev click handlers
next.addEventListener('click', function() {
    let items = document.querySelectorAll('.item');
    slider.appendChild(items[0]);
    updateActiveItemIndex(activeItemIndex + 1);
});

prev.addEventListener('click', function() {
    let items = document.querySelectorAll('.item');
    slider.prepend(items[items.length - 1]);
    updateActiveItemIndex(activeItemIndex - 1);
});

// Add event listeners for dropdown options
const dropdownOptions = dropdown.querySelectorAll("button");
dropdownOptions.forEach(option => {
  option.addEventListener("click", updateDropdownValue);
});

dropdownBtn.addEventListener("click", toggleDropdown);
document.body.addEventListener("click", dropdownOutsideClick);

document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    const formData = new FormData(this);
    const submitButton = document.querySelector('#btn-submit');
    const submitButtonText = document.querySelector('#btn-submit .button-text');

    // Show processing state
    submitButton.classList.add('loading');
    submitButtonText.textContent = 'Processing...';

    fetch('/process', {
        method: 'POST',
        body: formData
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }

        // First, add the downloaded garment image to the slider
        addImageToSlider(data.garment_image);

        // Wait for the final result image to be processed
        return fetch(`/result/${data.result}`);
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.blob();
    })
    .then(blob => {
        const url = URL.createObjectURL(blob);
        // Replace the garment image with the final output
        addImageToSlider(url);
        submitButton.classList.remove('loading');
        submitButtonText.textContent = 'Try Outfit!';
    })
    .catch(error => {
        console.error('Error:', error);
        submitButton.classList.remove('loading');
        submitButtonText.textContent = 'Try Outfit!';
        // Handle error display here
    });
});

function processImage(operation) {
    const button = document.querySelector(`#${operation}-btn`);
    const buttonText = button.querySelector('.button-text');
    button.classList.add('loading');
    buttonText.textContent = `${operation.charAt(0).toUpperCase() + operation.slice(1)}ing...`;

    return new Promise(async (resolve, reject) => {
        try {
            const slider = document.querySelector('.slide');
            const mainImage = slider.firstChild;
            const style = window.getComputedStyle(mainImage);
            const backgroundImage = style.getPropertyValue('background-image');
            const imageUrl = backgroundImage.replace(/^url\(['"](.+)['"]\)/, '$1');
            console.log(`${operation} URL:`, imageUrl);

            let blob;
            if (imageUrl.startsWith('blob:')) {
                const response = await fetch(imageUrl);
                blob = await response.blob();
            } else if (imageUrl.startsWith('data:')) {
                const base64Data = imageUrl.split(',')[1];
                const binaryString = atob(base64Data);
                const byteArray = new Uint8Array(binaryString.length);
                for (let i = 0; i < binaryString.length; i++) {
                    byteArray[i] = binaryString.charCodeAt(i);
                }
                blob = new Blob([byteArray], { type: 'image/jpeg' });
            } else {
                throw new Error('Unsupported image URL format');
            }

            const formData = new FormData();
            formData.append('file', blob, 'image.jpg');
            formData.append('operation', operation);

            const uploadResponse = await fetch('/operations', {
                method: 'POST',
                body: formData
            });

            if (!uploadResponse.ok) {
                throw new Error(`HTTP error! status: ${uploadResponse.status}`);
            }

            const data = await uploadResponse.json();
            if (data.error) {
                throw new Error(data.error);
            }

            if (data.processed_image) {
                addImageToSlider(data.processed_image);
                resolve(data.processed_image);
            } else {
                reject(new Error('No processed image received'));
            }
        } catch (error) {
            console.error('Error:', error);
            reject(error);
        } finally {
            button.classList.remove('loading');
            buttonText.textContent = operation.charAt(0).toUpperCase() + operation.slice(1);
        }
    });
}

document.getElementById('upscale-btn').addEventListener('click', () => processImage('upscale'));
document.getElementById('expand-btn').addEventListener('click', () => processImage('expand'));
