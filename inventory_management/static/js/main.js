// Main JavaScript file for Inventory Management System

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert-dismissible');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Movement form logic
    const fromLocationSelect = document.getElementById('from_location');
    const toLocationSelect = document.getElementById('to_location');
    
    if (fromLocationSelect && toLocationSelect) {
        function updateMovementType() {
            const fromValue = fromLocationSelect.value;
            const toValue = toLocationSelect.value;
            
            let movementType = '';
            let alertClass = '';
            
            if (fromValue && toValue) {
                movementType = 'Transfer';
                alertClass = 'alert-primary';
            } else if (toValue && !fromValue) {
                movementType = 'Stock In';
                alertClass = 'alert-success';
            } else if (fromValue && !toValue) {
                movementType = 'Stock Out';
                alertClass = 'alert-danger';
            }
            
            // Update movement type indicator if it exists
            const typeIndicator = document.getElementById('movement-type-indicator');
            if (typeIndicator) {
                typeIndicator.className = `alert ${alertClass}`;
                typeIndicator.innerHTML = `<i class="fas fa-info-circle"></i> Movement Type: <strong>${movementType}</strong>`;
                typeIndicator.style.display = movementType ? 'block' : 'none';
            }
        }
        
        fromLocationSelect.addEventListener('change', updateMovementType);
        toLocationSelect.addEventListener('change', updateMovementType);
        
        // Initial call
        updateMovementType();
    }

    // Table sorting functionality
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(function(header) {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = header.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const column = header.dataset.sort;
            const currentOrder = header.dataset.order || 'asc';
            const newOrder = currentOrder === 'asc' ? 'desc' : 'asc';
            
            // Sort rows
            rows.sort(function(a, b) {
                const aValue = a.querySelector(`td[data-${column}]`)?.textContent || '';
                const bValue = b.querySelector(`td[data-${column}]`)?.textContent || '';
                
                if (newOrder === 'asc') {
                    return aValue.localeCompare(bValue);
                } else {
                    return bValue.localeCompare(aValue);
                }
            });
            
            // Update table
            rows.forEach(function(row) {
                tbody.appendChild(row);
            });
            
            // Update header
            header.dataset.order = newOrder;
            
            // Update sort indicators
            sortableHeaders.forEach(function(h) {
                h.classList.remove('sort-asc', 'sort-desc');
            });
            header.classList.add(`sort-${newOrder}`);
        });
    });

    // Search functionality
    const searchInput = document.getElementById('table-search');
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            const table = document.querySelector('table tbody');
            const rows = table.querySelectorAll('tr');
            
            rows.forEach(function(row) {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(searchTerm) ? '' : 'none';
            });
        });
    }

    // Confirmation dialogs for delete actions
    const deleteButtons = document.querySelectorAll('[data-confirm]');
    deleteButtons.forEach(function(button) {
        button.addEventListener('click', function(event) {
            const message = this.dataset.confirm || 'Are you sure you want to delete this item?';
            if (!confirm(message)) {
                event.preventDefault();
            }
        });
    });

    // Auto-refresh for dashboard (every 30 seconds)
    if (window.location.pathname === '/') {
        setInterval(function() {
            // Only refresh if the page is visible
            if (!document.hidden) {
                location.reload();
            }
        }, 30000);
    }

    // Print functionality
    window.printReport = function() {
        window.print();
    };

    // Export functionality (if needed)
    window.exportTable = function(tableId, filename) {
        const table = document.getElementById(tableId);
        if (!table) return;
        
        let csv = [];
        const rows = table.querySelectorAll('tr');
        
        rows.forEach(function(row) {
            const cols = row.querySelectorAll('td, th');
            const rowData = [];
            cols.forEach(function(col) {
                rowData.push('"' + col.textContent.replace(/"/g, '""') + '"');
            });
            csv.push(rowData.join(','));
        });
        
        const csvContent = csv.join('\n');
        const blob = new Blob([csvContent], { type: 'text/csv' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename || 'export.csv';
        a.click();
        window.URL.revokeObjectURL(url);
    };

    // Loading states for forms
    const submitButtons = document.querySelectorAll('button[type="submit"]');
    submitButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            const form = this.closest('form');
            if (form && form.checkValidity()) {
                this.innerHTML = '<span class="loading"></span> Processing...';
                this.disabled = true;
            }
        });
    });

    // Keyboard shortcuts
    document.addEventListener('keydown', function(event) {
        // Ctrl/Cmd + N for new item
        if ((event.ctrlKey || event.metaKey) && event.key === 'n') {
            event.preventDefault();
            const addButton = document.querySelector('a[href*="/add"]');
            if (addButton) {
                addButton.click();
            }
        }
        
        // Escape to go back
        if (event.key === 'Escape') {
            const backButton = document.querySelector('a[href*="back"], .btn-secondary');
            if (backButton) {
                backButton.click();
            }
        }
    });

    // Responsive table handling
    function makeTablesResponsive() {
        const tables = document.querySelectorAll('table:not(.table-responsive table)');
        tables.forEach(function(table) {
            if (!table.closest('.table-responsive')) {
                const wrapper = document.createElement('div');
                wrapper.className = 'table-responsive';
                table.parentNode.insertBefore(wrapper, table);
                wrapper.appendChild(table);
            }
        });
    }
    
    makeTablesResponsive();

    // Clickable table rows with ripple effect
    const tables = document.querySelectorAll('table');
    tables.forEach(function(table) {
        table.addEventListener('click', function(e) {
            const target = e.target;
            // Avoid triggering on interactive elements
            if (target.closest('a, button, input, select, textarea, label')) return;
            const row = target.closest('tr.clickable-row');
            if (!row) return;

            // Ripple effect
            row.classList.add('ripple');
            const rect = row.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            row.style.setProperty('--ripple-x', x + 'px');
            row.style.setProperty('--ripple-y', y + 'px');
            row.classList.remove('animate');
            // force reflow
            void row.offsetWidth;
            row.classList.add('animate');

            const href = row.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });

        // Keyboard accessibility (Enter)
        table.addEventListener('keydown', function(e) {
            if (e.key !== 'Enter') return;
            const row = e.target.closest('tr.clickable-row');
            if (!row) return;
            const href = row.dataset.href;
            if (href) {
                window.location.href = href;
            }
        });
    });

    // Initialize any additional components
    console.log('Inventory Management System initialized successfully');
});
