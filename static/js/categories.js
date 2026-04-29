// ================================
//  CATEGORIAS - Pedro Finance
// ================================

// -------- APLICAR CORES DINÂMICAS --------
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.category-card').forEach(card => {
        const color = card.dataset.color;
        card.style.setProperty('--cat-color', color);
    });

    document.querySelectorAll('.category-icon[data-cat-color]').forEach(icon => {
        const color = icon.dataset.catColor;
        icon.style.backgroundColor = hexToRgba(color, 0.12);
        icon.style.color = color;
    });

    updatePreview();
});

// -------- UTILITÁRIO: HEX PARA RGBA --------
function hexToRgba(hex, alpha) {
    const r = parseInt(hex.slice(1, 3), 16);
    const g = parseInt(hex.slice(3, 5), 16);
    const b = parseInt(hex.slice(5, 7), 16);
    return `rgba(${r}, ${g}, ${b}, ${alpha})`;
}

// -------- MODAL CRIAR --------
function openCreateModal() {
    const modal = document.getElementById('categoryModal');
    const form = document.getElementById('categoryForm');
    const title = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('modalSubmitBtn');

    // Reset completo
    form.action = '/categories/create';
    document.getElementById('catName').value = '';
    document.getElementById('catType').value = 'despesa';
    title.textContent = 'Nova Categoria';
    submitBtn.textContent = 'Criar Categoria';

    resetIconSelection('📁');
    resetColorSelection('#EF4444');
    updatePreview();

    modal.classList.add('active');
    document.getElementById('catName').focus();
}

// -------- MODAL EDITAR --------
async function openEditModal(categoryId) {
    const modal = document.getElementById('categoryModal');
    const form = document.getElementById('categoryForm');
    const title = document.getElementById('modalTitle');
    const submitBtn = document.getElementById('modalSubmitBtn');

    try {
        const response = await fetch(`/categories/${categoryId}/json`);
        if (!response.ok) throw new Error('Erro ao buscar categoria');

        const cat = await response.json();

        form.action = `/categories/edit/${categoryId}`;
        title.textContent = 'Editar Categoria';
        submitBtn.textContent = 'Salvar Alterações';

        document.getElementById('catName').value = cat.name;
        document.getElementById('catType').value = cat.type;

        resetIconSelection(cat.icon);
        resetColorSelection(cat.color);
        updatePreview();

        modal.classList.add('active');
        document.getElementById('catName').focus();
    } catch (error) {
        console.error(error);
        alert('Erro ao carregar dados da categoria.');
    }
}

// -------- MODAL EXCLUIR --------
function openDeleteModal(categoryId, categoryName, transactionCount) {
    const modal = document.getElementById('deleteModal');
    const form = document.getElementById('deleteForm');
    const nameEl = document.getElementById('deleteCatName');
    const detailEl = document.getElementById('deleteWarningDetail');

    transactionCount = parseInt(transactionCount) || 0;

    form.action = `/categories/delete/${categoryId}`;
    nameEl.textContent = categoryName;

    if (transactionCount > 0) {
        const label = transactionCount === 1 ? '1 transação vinculada' : `${transactionCount} transações vinculadas`;
        detailEl.textContent = `Esta categoria possui ${label}. Elas ficarão sem categoria.`;
    } else {
        detailEl.textContent = 'Esta ação não pode ser desfeita.';
    }

    modal.classList.add('active');
}

// -------- FECHAR MODAIS --------
function closeModal() {
    document.getElementById('categoryModal').classList.remove('active');
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('active');
}

// Fechar ao clicar no overlay
document.querySelectorAll('.modal-overlay').forEach(overlay => {
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            overlay.classList.remove('active');
        }
    });
});

// Fechar com ESC
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
        closeDeleteModal();
    }
});

// -------- ICON PICKER --------
function resetIconSelection(icon) {
    const picker = document.getElementById('iconPicker');
    const hidden = document.getElementById('catIcon');

    let found = false;
    picker.querySelectorAll('.icon-option').forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.icon === icon) {
            btn.classList.add('selected');
            found = true;
        }
    });

    if (!found) {
        const first = picker.querySelector('.icon-option');
        if (first) {
            first.classList.add('selected');
            icon = first.dataset.icon;
        }
    }

    hidden.value = icon;
}

document.getElementById('iconPicker').addEventListener('click', (e) => {
    const btn = e.target.closest('.icon-option');
    if (!btn) return;

    document.querySelectorAll('#iconPicker .icon-option').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    document.getElementById('catIcon').value = btn.dataset.icon;
    updatePreview();
});

// -------- COLOR PICKER --------
function resetColorSelection(color) {
    const picker = document.getElementById('colorPicker');
    const hidden = document.getElementById('catColor');

    let found = false;
    picker.querySelectorAll('.color-option').forEach(btn => {
        btn.classList.remove('selected');
        if (btn.dataset.color === color) {
            btn.classList.add('selected');
            found = true;
        }
    });

    if (!found) {
        const first = picker.querySelector('.color-option');
        if (first) {
            first.classList.add('selected');
            color = first.dataset.color;
        }
    }

    hidden.value = color;
}

document.getElementById('colorPicker').addEventListener('click', (e) => {
    const btn = e.target.closest('.color-option');
    if (!btn) return;

    document.querySelectorAll('#colorPicker .color-option').forEach(b => b.classList.remove('selected'));
    btn.classList.add('selected');
    document.getElementById('catColor').value = btn.dataset.color;
    updatePreview();
});

// -------- PREVIEW EM TEMPO REAL --------
function updatePreview() {
    const name = document.getElementById('catName').value.trim() || 'Nome da categoria';
    const type = document.getElementById('catType').value;
    const icon = document.getElementById('catIcon').value;
    const color = document.getElementById('catColor').value;

    const previewIcon = document.getElementById('previewIcon');
    const previewName = document.getElementById('previewName');
    const previewType = document.getElementById('previewType');

    previewIcon.textContent = icon;
    previewIcon.style.backgroundColor = hexToRgba(color, 0.12);
    previewIcon.style.color = color;

    previewName.textContent = name;
    previewType.textContent = type === 'receita' ? '🟢 Receita' : '🔴 Despesa';
}

// Listeners para atualizar preview
document.getElementById('catName').addEventListener('input', updatePreview);
document.getElementById('catType').addEventListener('change', updatePreview);

// -------- AUTO-FECHAR FLASH MESSAGES --------
setTimeout(() => {
    document.querySelectorAll('.flash-message').forEach(msg => {
        msg.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
        msg.style.opacity = '0';
        msg.style.transform = 'translateY(-10px)';
        setTimeout(() => msg.remove(), 300);
    });
}, 4000);
