let dragData = null;
let currentlyEditing = null;
let selectedCard = null;

// Drag and Drop Functions
function allowDrop(ev) {
  ev.preventDefault();
  const col = ev.currentTarget;
  col.classList.add('drop-highlight');
}

function dragCard(ev){
  const card = ev.target.closest(".card");
  if(card.classList.contains('editing')) {
    ev.preventDefault();
    return;
  }
  dragData = { cardId: card.dataset.card };
  ev.dataTransfer.setData("text/plain", dragData.cardId);
  card.classList.add('dragging');

  // Create custom drag image
  const dragImage = card.cloneNode(true);
  dragImage.style.transform = 'rotate(5deg)';
  dragImage.style.opacity = '0.8';
  document.body.appendChild(dragImage);
  ev.dataTransfer.setDragImage(dragImage, 0, 0);
  setTimeout(() => document.body.removeChild(dragImage), 0);
}

function dragEnd(ev) {
  const card = ev.target.closest(".card");
  card.classList.remove('dragging');
  document.querySelectorAll('.col').forEach(col => col.classList.remove('drop-highlight'));
}

async function dropCard(ev){
  ev.preventDefault();
  const col = ev.currentTarget;
  const colId = col.dataset.col;
  const cardId = ev.dataTransfer.getData("text/plain");
  if(!cardId || !colId) return;
  
  const cardEl = document.querySelector(`.card[data-card="${cardId}"]`);
  cardEl.style.opacity = '1';
  
  const dropZone = col.querySelector(".drop");
  dropZone.appendChild(cardEl);
  
  // Add slide animation
  cardEl.style.transform = 'translateY(-10px)';
  setTimeout(() => {
    cardEl.style.transform = 'translateY(0)';
  }, 50);
  
  await fetch(`/move/${cardId}`, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify({column_id: parseInt(colId,10), position: Array.from(col.querySelectorAll(".card")).indexOf(cardEl)})
  });
}

// Add Card Function
async function addCard(columnId) {
  try {
    const response = await fetch('/cards', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `column_id=${columnId}&title=New Card&notes=`
    });
    
    if (response.ok) {
      const cardHtml = await response.text();
      const dropZone = document.getElementById(`col-${columnId}`);
      
      // Create temporary element to parse HTML
      const temp = document.createElement('div');
      temp.innerHTML = cardHtml;
      const newCard = temp.firstElementChild;
      
      // Insert at beginning of drop zone
      dropZone.insertBefore(newCard, dropZone.firstChild);
      
      // Animate in
      newCard.style.transform = 'translateY(-20px)';
      newCard.style.opacity = '0';
      setTimeout(() => {
        newCard.style.transform = 'translateY(0)';
        newCard.style.opacity = '1';
      }, 50);
      
      // Immediately enter edit mode
      setTimeout(() => editCard(newCard), 100);
      
      // Update card count
      updateCardCount(columnId);
    }
  } catch (error) {
    console.error('Error adding card:', error);
  }
}

// Edit Card Function
function editCard(cardElement) {
  if (currentlyEditing) {
    saveCard(currentlyEditing);
  }

  currentlyEditing = cardElement;
  cardElement.classList.add('editing');

  const titleElement = cardElement.querySelector('strong');
  const notesElement = cardElement.querySelector('.card-notes');
  const cardId = cardElement.dataset.card;

  // Store original values
  const originalTitle = titleElement.textContent;
  const originalNotes = notesElement ? notesElement.textContent : '';

  // Create editable elements
  const titleInput = document.createElement('input');
  titleInput.type = 'text';
  titleInput.value = originalTitle;
  titleInput.className = 'card-title-input';
  titleInput.style.fontWeight = 'bold';
  titleInput.dataset.original = originalTitle;

  const notesTextarea = document.createElement('textarea');
  notesTextarea.value = originalNotes;
  notesTextarea.className = 'card-notes-input';
  notesTextarea.rows = 3;
  notesTextarea.style.fontSize = '12px';
  notesTextarea.style.color = '#666';
  notesTextarea.style.marginTop = '4px';
  notesTextarea.placeholder = 'Add notes...';
  notesTextarea.dataset.original = originalNotes;

  // Create action buttons
  const actionDiv = document.createElement('div');
  actionDiv.className = 'edit-actions';
  actionDiv.innerHTML = `
    <button type="button" class="save-btn" onclick="saveCard(currentlyEditing)">Save</button>
    <button type="button" class="cancel-btn" onclick="cancelEdit(currentlyEditing)">Cancel</button>
    <span class="edit-hint">Enter to save • Escape to cancel</span>
  `;

  // Replace elements
  titleElement.replaceWith(titleInput);
  if (notesElement) {
    notesElement.replaceWith(notesTextarea);
  } else {
    titleInput.after(notesTextarea);
  }
  notesTextarea.after(actionDiv);

  // Focus and select title
  titleInput.focus();
  titleInput.select();

  // Auto-resize textarea
  notesTextarea.addEventListener('input', autoResizeTextarea);
  autoResizeTextarea.call(notesTextarea);

  // Event handlers
  titleInput.addEventListener('keydown', handleEditKeydown);
  notesTextarea.addEventListener('keydown', handleEditKeydown);
  titleInput.addEventListener('input', debounce(() => autoSaveCard(cardElement), 1000));
  notesTextarea.addEventListener('input', debounce(() => autoSaveCard(cardElement), 1000));
}

function autoResizeTextarea() {
  this.style.height = 'auto';
  this.style.height = this.scrollHeight + 'px';
}

// Auto-save functionality
function autoSaveCard(cardElement) {
  if (!cardElement || !cardElement.classList.contains('editing')) return;

  const titleInput = cardElement.querySelector('.card-title-input');
  const title = titleInput ? titleInput.value.trim() : '';

  if (title && title !== titleInput.dataset.original) {
    showToast('Auto-saving...', 'info', 1000);
    saveCard(cardElement, true);
  }
}

function handleEditKeydown(ev) {
  if (ev.key === 'Enter' && !ev.shiftKey) {
    ev.preventDefault();
    saveCard(currentlyEditing);
  } else if (ev.key === 'Escape') {
    ev.preventDefault();
    cancelEdit(currentlyEditing);
  }
}

async function saveCard(cardElement, isAutoSave = false) {
  if (!cardElement || !cardElement.classList.contains('editing')) return;

  const titleInput = cardElement.querySelector('.card-title-input');
  const notesInput = cardElement.querySelector('.card-notes-input');
  const cardId = cardElement.dataset.card;

  if (!titleInput) return;

  const title = titleInput.value.trim();
  const notes = notesInput ? notesInput.value.trim() : '';

  if (!title) {
    if (!isAutoSave) {
      showToast('Title cannot be empty', 'error');
      titleInput.focus();
    }
    return;
  }

  showLoadingState(cardElement, true);

  try {
    const response = await fetch(`/cards/${cardId}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: `title=${encodeURIComponent(title)}&notes=${encodeURIComponent(notes)}`
    });

    if (response.ok) {
      const updatedCardHtml = await response.text();
      const temp = document.createElement('div');
      temp.innerHTML = updatedCardHtml;
      const updatedCard = temp.firstElementChild;

      // Animate the update
      cardElement.style.transform = 'scale(1.02)';
      setTimeout(() => {
        cardElement.replaceWith(updatedCard);
        currentlyEditing = null;
        showToast(isAutoSave ? 'Auto-saved' : 'Card saved', 'success');
      }, 100);
    } else {
      throw new Error('Failed to save card');
    }
  } catch (error) {
    console.error('Error saving card:', error);
    showToast('Failed to save card', 'error');
  } finally {
    showLoadingState(cardElement, false);
  }
}

function cancelEdit(cardElement) {
  if (!cardElement || !cardElement.classList.contains('editing')) return;

  const titleInput = cardElement.querySelector('.card-title-input');
  const notesInput = cardElement.querySelector('.card-notes-input');
  const actionDiv = cardElement.querySelector('.edit-actions');

  // Restore original values
  const originalTitle = titleInput.dataset.original;
  const originalNotes = notesInput.dataset.original;

  const titleElement = document.createElement('strong');
  titleElement.textContent = originalTitle;

  const notesElement = document.createElement('div');
  notesElement.className = 'card-notes muted';
  notesElement.textContent = originalNotes;

  titleInput.replaceWith(titleElement);
  notesInput.replaceWith(notesElement);
  if (actionDiv) actionDiv.remove();

  cardElement.classList.remove('editing');
  currentlyEditing = null;
}

// Update card count in column header
function updateCardCount(columnId) {
  const column = document.querySelector(`[data-col="${columnId}"]`);
  const cards = column.querySelectorAll('.card');
  const countElement = column.querySelector('.card-count');
  if (countElement) {
    countElement.textContent = `(${cards.length})`;
  }
}

// Quick Actions
async function quickDelete(cardId) {
  if (!confirm('Delete this card?')) return;
  
  try {
    const response = await fetch(`/cards/${cardId}`, {
      method: 'DELETE'
    });
    
    if (response.ok) {
      const cardElement = document.querySelector(`[data-card="${cardId}"]`);
      cardElement.style.transform = 'scale(0.8)';
      cardElement.style.opacity = '0';
      setTimeout(() => {
        cardElement.remove();
        // Update card counts
        document.querySelectorAll('.col').forEach(col => {
          const colId = col.dataset.col;
          updateCardCount(colId);
        });
      }, 200);
    }
  } catch (error) {
    console.error('Error deleting card:', error);
  }
}

async function quickMove(cardId, newColumnId) {
  if (!newColumnId) return;
  
  try {
    const cardElement = document.querySelector(`[data-card="${cardId}"]`);
    const oldColumn = cardElement.closest('.col');
    const newColumn = document.querySelector(`[data-col="${newColumnId}"]`);
    const newDropZone = newColumn.querySelector('.drop');
    
    // Move the card visually
    newDropZone.appendChild(cardElement);
    
    // Animate the move
    cardElement.style.transform = 'scale(1.05)';
    setTimeout(() => {
      cardElement.style.transform = 'scale(1)';
    }, 150);
    
    // Update backend
    const response = await fetch(`/move/${cardId}`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        column_id: parseInt(newColumnId, 10), 
        position: 0
      })
    });
    
    if (response.ok) {
      // Update card counts
      updateCardCount(oldColumn.dataset.col);
      updateCardCount(newColumnId);
    }
  } catch (error) {
    console.error('Error moving card:', error);
  }
}

// Event delegation for card clicking
document.addEventListener('click', function(ev) {
  const card = ev.target.closest('.card');
  if (card && !card.classList.contains('editing') && !ev.target.closest('button') && !ev.target.closest('form') && !ev.target.closest('select')) {
    editCard(card);
  }
});

// Utility Functions
function debounce(func, wait) {
  let timeout;
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout);
      func(...args);
    };
    clearTimeout(timeout);
    timeout = setTimeout(later, wait);
  };
}

function showToast(message, type = 'info', duration = 3000) {
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  toast.textContent = message;

  const container = document.getElementById('toast-container');
  container.appendChild(toast);

  // Animate in
  setTimeout(() => toast.classList.add('toast-show'), 100);

  // Remove after duration
  setTimeout(() => {
    toast.classList.remove('toast-show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

function showLoadingState(element, isLoading) {
  if (isLoading) {
    element.classList.add('loading');
  } else {
    element.classList.remove('loading');
  }
}

// Card selection functionality
function selectCard(cardElement) {
  if (selectedCard) {
    selectedCard.classList.remove('selected');
  }
  selectedCard = cardElement;
  cardElement.classList.add('selected');
}

// Keyboard shortcuts
document.addEventListener('keydown', function(ev) {
  // Don't interfere with form inputs
  if (ev.target.tagName.toLowerCase() === 'input' || ev.target.tagName.toLowerCase() === 'textarea') {
    return;
  }

  // Global shortcuts
  switch(ev.key) {
    case 'n':
    case 'N':
      // Add to first column (Todo)
      const firstCol = document.querySelector('.col');
      const colId = firstCol.dataset.col;
      addCard(colId);
      ev.preventDefault();
      break;

    case 'Escape':
      if (currentlyEditing) {
        cancelEdit(currentlyEditing);
        ev.preventDefault();
      }
      break;

    case 'Delete':
    case 'Backspace':
      if (selectedCard && !currentlyEditing) {
        const cardId = selectedCard.dataset.card;
        quickDelete(cardId);
        ev.preventDefault();
      }
      break;

    case '1':
    case '2':
    case '3':
      if (selectedCard && !currentlyEditing) {
        const cardId = selectedCard.dataset.card;
        quickMove(cardId, ev.key);
        ev.preventDefault();
      }
      break;

    case 'Enter':
      if (selectedCard && !currentlyEditing) {
        editCard(selectedCard);
        ev.preventDefault();
      }
      break;
  }
});

// Checklist Management Functions
async function toggleChecklistItem(itemId, button) {
  const listItem = button.closest('li');
  const isChecked = button.textContent === '☑';

  // Optimistic update
  button.textContent = isChecked ? '☐' : '☑';
  const textSpan = listItem.querySelector('.checklist-text');
  textSpan.classList.toggle('done');
  listItem.classList.toggle('checked');

  try {
    const response = await fetch(`/toggle/${itemId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'}
    });

    if (!response.ok) {
      // Revert on error
      button.textContent = isChecked ? '☑' : '☐';
      textSpan.classList.toggle('done');
      listItem.classList.toggle('checked');
      showToast('Failed to update item', 'error');
    } else {
      // Update progress bar
      updateChecklistProgress(button.closest('.card'));
    }
  } catch (error) {
    console.error('Error toggling checklist item:', error);
    showToast('Failed to update item', 'error');
  }
}

async function addChecklistItem(event, cardId) {
  event.preventDefault();
  const form = event.target;
  const input = form.querySelector('input[name="text"]');
  const text = input.value.trim();

  if (!text) return;

  try {
    const response = await fetch(`/checklist/${cardId}`, {
      method: 'POST',
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: `text=${encodeURIComponent(text)}`
    });

    if (response.ok) {
      const itemHtml = await response.text();
      const checklistUl = document.getElementById(`checklist-${cardId}`);

      if (checklistUl) {
        // Add to existing checklist
        checklistUl.insertAdjacentHTML('beforeend', itemHtml);
      } else {
        // Replace card (first checklist item)
        location.reload(); // Temporary - should replace with better solution
      }

      input.value = '';
      updateChecklistProgress(form.closest('.card'));
      showToast('Item added', 'success', 1500);
    }
  } catch (error) {
    console.error('Error adding checklist item:', error);
    showToast('Failed to add item', 'error');
  }
}

async function deleteChecklistItem(itemId, button) {
  if (!confirm('Delete this checklist item?')) return;

  const listItem = button.closest('li');

  try {
    const response = await fetch(`/checklist-item/${itemId}`, {
      method: 'DELETE'
    });

    if (response.ok) {
      listItem.style.opacity = '0';
      listItem.style.transform = 'translateX(-20px)';
      setTimeout(() => {
        listItem.remove();
        updateChecklistProgress(button.closest('.card'));
      }, 200);
      showToast('Item deleted', 'success', 1500);
    }
  } catch (error) {
    console.error('Error deleting checklist item:', error);
    showToast('Failed to delete item', 'error');
  }
}

function updateChecklistProgress(card) {
  const checklistItems = card.querySelectorAll('.checklist li');
  const checkedItems = card.querySelectorAll('.checklist li.checked');

  const summary = card.querySelector('.checklist-details summary');
  if (summary && checklistItems.length > 0) {
    summary.textContent = `Checklist (${checkedItems.length}/${checklistItems.length})`;
  }

  const progressBar = card.querySelector('.checklist-fill');
  if (progressBar && checklistItems.length > 0) {
    const progress = (checkedItems.length / checklistItems.length) * 100;
    progressBar.style.width = `${progress}%`;
  }
}

// Search functionality
function initSearch() {
  const searchInput = document.getElementById('search-input');
  if (searchInput) {
    searchInput.addEventListener('input', debounce(function() {
      const query = this.value.toLowerCase();
      const cards = document.querySelectorAll('.card');

      cards.forEach(card => {
        const title = card.querySelector('strong').textContent.toLowerCase();
        const notes = card.querySelector('.card-notes');
        const notesText = notes ? notes.textContent.toLowerCase() : '';

        if (title.includes(query) || notesText.includes(query)) {
          card.style.display = '';
          card.classList.remove('filtered-out');
        } else {
          card.style.display = query ? 'none' : '';
          card.classList.toggle('filtered-out', !!query);
        }
      });
    }, 300));
  }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
  initSearch();

  // Add event listeners for card selection
  document.addEventListener('click', function(ev) {
    const card = ev.target.closest('.card');
    if (card && !card.classList.contains('editing') &&
        !ev.target.closest('button') && !ev.target.closest('form') &&
        !ev.target.closest('select') && !ev.target.closest('input')) {
      selectCard(card);
      // Double-click to edit
      if (ev.detail === 2) {
        editCard(card);
      }
    }
  });
});
