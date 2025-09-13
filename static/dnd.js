let dragData = null;
let currentlyEditing = null;

// Drag and Drop Functions
function dragCard(ev){
  const card = ev.target.closest(".card");
  if(card.classList.contains('editing')) {
    ev.preventDefault();
    return;
  }
  dragData = { cardId: card.dataset.card };
  ev.dataTransfer.setData("text/plain", dragData.cardId);
  card.style.opacity = '0.5';
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
  const notesElement = cardElement.querySelector('.muted');
  const cardId = cardElement.dataset.card;
  
  // Create editable elements
  const titleInput = document.createElement('input');
  titleInput.type = 'text';
  titleInput.value = titleElement.textContent;
  titleInput.className = 'card-title-input';
  titleInput.style.fontWeight = 'bold';
  
  const notesTextarea = document.createElement('textarea');
  notesTextarea.value = notesElement ? notesElement.textContent : '';
  notesTextarea.className = 'card-notes-input';
  notesTextarea.rows = 2;
  notesTextarea.style.fontSize = '12px';
  notesTextarea.style.color = '#666';
  notesTextarea.style.marginTop = '4px';
  notesTextarea.placeholder = 'Add notes...';
  
  // Replace elements
  titleElement.replaceWith(titleInput);
  if (notesElement) {
    notesElement.replaceWith(notesTextarea);
  } else {
    titleInput.after(notesTextarea);
  }
  
  // Focus and select title
  titleInput.focus();
  titleInput.select();
  
  // Event handlers
  titleInput.addEventListener('keydown', handleEditKeydown);
  notesTextarea.addEventListener('keydown', handleEditKeydown);
  titleInput.addEventListener('blur', () => setTimeout(() => saveCard(cardElement), 100));
  notesTextarea.addEventListener('blur', () => setTimeout(() => saveCard(cardElement), 100));
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

async function saveCard(cardElement) {
  if (!cardElement || !cardElement.classList.contains('editing')) return;
  
  const titleInput = cardElement.querySelector('.card-title-input');
  const notesInput = cardElement.querySelector('.card-notes-input');
  const cardId = cardElement.dataset.card;
  
  if (!titleInput) return;
  
  const title = titleInput.value.trim();
  const notes = notesInput ? notesInput.value.trim() : '';
  
  if (!title) {
    titleInput.focus();
    return;
  }
  
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
      
      cardElement.replaceWith(updatedCard);
      currentlyEditing = null;
    }
  } catch (error) {
    console.error('Error saving card:', error);
  }
}

function cancelEdit(cardElement) {
  // Reload the card to cancel changes
  location.reload();
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

// Keyboard shortcuts
document.addEventListener('keydown', function(ev) {
  if (ev.target.tagName.toLowerCase() === 'input' || ev.target.tagName.toLowerCase() === 'textarea') {
    return;
  }
  
  if (ev.key === 'n' || ev.key === 'N') {
    // Add to first column (Todo)
    const firstCol = document.querySelector('.col');
    const colId = firstCol.dataset.col;
    addCard(colId);
    ev.preventDefault();
  }
  
  if (ev.key === 'Escape' && currentlyEditing) {
    cancelEdit(currentlyEditing);
    ev.preventDefault();
  }
});
