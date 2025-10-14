document.addEventListener('DOMContentLoaded', () => {
    const goalInput = document.getElementById('goal-input');
    const planButton = document.getElementById('plan-button');
    const loadingSpinner = document.getElementById('loading-spinner');
    const planOutput = document.getElementById('plan-output');
    const taskList = document.getElementById('task-list');
    const errorMessage = document.getElementById('error-message');

    // Base URL for the Flask backend (ensure this matches your Flask port)
    const API_BASE_URL = 'http://127.0.0.1:5000/api/generate-plan';

    planButton.addEventListener('click', generateTaskPlan);

    async function generateTaskPlan() {
        const goal = goalInput.value.trim();
        if (!goal) {
            displayError('Please enter a goal to plan!');
            return;
        }

        // Reset display
        taskList.innerHTML = '';
        planOutput.classList.add('hidden');
        errorMessage.classList.add('hidden');
        loadingSpinner.classList.remove('hidden');
        planButton.disabled = true;

        try {
            const response = await fetch(API_BASE_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ goal: goal }),
            });

            const data = await response.json();

            if (!response.ok) {
                // Handle API errors (e.g., 400, 500)
                throw new Error(data.error || `Server responded with status: ${response.status}`);
            }

            if (data && Array.isArray(data)) {
                displayTaskPlan(data);
            } else {
                // Fallback for unexpected JSON format
                throw new Error('AI returned an unexpected format. Try a different goal.');
            }

        } catch (error) {
            console.error('Fetch error:', error);
            displayError(`Failed to connect or process: ${error.message}`);
        } finally {
            loadingSpinner.classList.add('hidden');
            planButton.disabled = false;
        }
    }

    function displayTaskPlan(tasks) {
        planOutput.classList.remove('hidden');
        
        tasks.forEach((task, index) => {
            // Apply staggered animation delay for a smoother reveal
            const delay = index * 0.1; // 100ms delay per card

            const taskCard = document.createElement('div');
            taskCard.classList.add('task-card');
            taskCard.style.animationDelay = `${delay}s`;

            const dependencyHtml = task.dependencies.length > 0
                ? `Dependencies: ${task.dependencies.map(dep => `<span class="dependency-tag">Task #${dep}</span>`).join('')}`
                : 'Dependencies: <span class="dependency-tag">None</span>';

            taskCard.innerHTML = `
                <h3>[Task #${task.task_id}] ${task.task_name}</h3>
                <p><strong>Deadline:</strong> ${task.deadline}</p>
                <p>${dependencyHtml}</p>
                <p><strong>Description:</strong> ${task.description}</p>
            `;
            taskList.appendChild(taskCard);
        });
    }

    function displayError(message) {
        errorMessage.textContent = `Error: ${message}`;
        errorMessage.classList.remove('hidden');
    }
});