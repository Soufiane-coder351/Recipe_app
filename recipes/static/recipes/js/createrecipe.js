let stepCount = 1;

// Function to add a new step
function addStep() {
    stepCount++;
    const stepsContainer = document.getElementById('stepsContainer');
    const newStep = document.createElement('div');
    newStep.classList.add('mb-4', 'step');
    newStep.innerHTML = `
        <label for="stepDescription${stepCount}" class="block text-gray-700 text-lg font-medium">Étape ${stepCount} - Description</label>
        <input type="text" class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-800" id="stepDescription${stepCount}" name="stepDescription${stepCount}" placeholder="Entrez la description de l'étape">

        <label for="stepImage${stepCount}" class="block text-gray-700 text-lg font-medium mt-2">Image de l'étape ${stepCount}</label>
        <input type="file" class="w-full px-4 py-2 border border-gray-300 rounded-lg bg-gray-50 text-gray-800" id="stepImage${stepCount}" name="stepImage${stepCount}" accept="image/*">
    `;
    stepsContainer.appendChild(newStep);
}

const addIngredientBtn = document.getElementById('addIngredientBtn');
const ingredientInput = document.getElementById('ingredientInput');
const ingredientsList = document.getElementById('ingredientsList');
let ingredientsInput = document.getElementById('ingredientsInput'); // The hidden input

addIngredientBtn.addEventListener('click', function () {
    const ingredientValue = ingredientInput.value.trim();
    if (ingredientValue) {
        // Create a span element for the tag
        const tag = document.createElement('span');
        tag.classList.add('inline-flex', 'items-center', 'bg-gray-600', 'text-white', 'text-sm', 'px-3', 'py-1', 'rounded-md');
        tag.textContent = ingredientValue;

        // Add a remove button to the tag
        const removeBtn = document.createElement('span');
        removeBtn.textContent = '×'; // Close icon
        removeBtn.classList.add('ml-2', 'text-gray-400', 'hover:text-white', 'cursor-pointer', 'text-sm', 'transition');
        removeBtn.style.display = 'inline-block';

        removeBtn.onclick = function () {
            ingredientsList.removeChild(tag);
            updateIngredients(); // Update the hidden input when an ingredient is removed
        };

        tag.appendChild(removeBtn);
        ingredientsList.appendChild(tag);

        ingredientsInput.value = ingredientValue;
        ingredientInput.value = ''; // Clear the input field
        // Update the hidden input with the comma-separated ingredients
        updateIngredients();
    }
});

// Function to update the hidden ingredients input field
function updateIngredients() {
    const tags = ingredientsList.getElementsByTagName('span');
    let ingredientsArray = [];
    for (let i = 0; i < tags.length; i++) {
        ingredientsArray.push(tags[i].textContent.trim().replace('×', '').trim());
    }
    console.log("ingredient for now are: ");
    console.log(ingredientsArray);
    // Join the ingredients with commas and update the hidden input value
    ingredientsInput.value = ingredientsArray.join(',');
}



// Function to set active category
function setActiveCategory(button) {
    const buttons = document.querySelectorAll('.category-btn');
    buttons.forEach(btn => {
        btn.classList.remove('bg-gray-500'); // Remove active state
    });
    button.classList.add('bg-gray-500'); // Add active state to the clicked button
}