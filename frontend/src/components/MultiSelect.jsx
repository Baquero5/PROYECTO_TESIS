import { useState, useRef, useEffect } from 'react';

export default function MultiSelect({
    items = [],
    selectedIds = [],
    onSelectionChange,
    placeholder = 'Seleccionar...',
    labelKey = 'label',
    valueKey = 'value',
    showSelectAll = true,
    searchPlaceholder = 'Buscar...',
}) {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const containerRef = useRef(null);

    useEffect(() => {
        const handleClickOutside = (e) => {
            if (containerRef.current && !containerRef.current.contains(e.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        document.addEventListener('touchstart', handleClickOutside);
        return () => {
            document.removeEventListener('mousedown', handleClickOutside);
            document.removeEventListener('touchstart', handleClickOutside);
        };
    }, []);

    const filteredItems = items.filter(item =>
        String(item[labelKey]).toLowerCase().includes(searchTerm.toLowerCase())
    );

    const allSelected = filteredItems.length > 0 && filteredItems.every(item => selectedIds.includes(item[valueKey]));
    const someSelected = selectedIds.length > 0 && !allSelected;

    const toggleItem = (id) => {
        const newSelected = selectedIds.includes(id)
            ? selectedIds.filter(s => s !== id)
            : [...selectedIds, id];
        onSelectionChange(newSelected);
    };

    const toggleAll = () => {
        if (allSelected) {
            onSelectionChange([]);
        } else {
            onSelectionChange(filteredItems.map(item => item[valueKey]));
        }
    };

    const getDisplayText = () => {
        if (selectedIds.length === 0) return placeholder;
        if (selectedIds.length === items.length) return `Todos (${items.length})`;
        if (selectedIds.length === 1) {
            const item = items.find(i => i[valueKey] === selectedIds[0]);
            return item ? String(item[labelKey]) : `${selectedIds.length} seleccionado`;
        }
        return `${selectedIds.length} seleccionados`;
    };

    return (
        <div ref={containerRef} style={{ position: 'relative', width: '100%' }}>
            <button
                type="button"
                onClick={() => setIsOpen(!isOpen)}
                style={{
                    width: '100%',
                    padding: '8px 32px 8px 12px',
                    borderRadius: '6px',
                    border: `1px solid ${isOpen ? 'var(--primary)' : 'var(--gray-300)'}`,
                    background: 'white',
                    textAlign: 'left',
                    cursor: 'pointer',
                    fontSize: '0.9rem',
                    color: selectedIds.length > 0 ? 'var(--gray-800)' : 'var(--gray-500)',
                    position: 'relative',
                    boxShadow: isOpen ? '0 0 0 2px var(--primary-light)' : 'none',
                    transition: 'all 0.2s',
                }}
            >
                {getDisplayText()}
                <span style={{
                    position: 'absolute',
                    right: '12px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    color: 'var(--gray-400)',
                    fontSize: '0.7rem',
                    pointerEvents: 'none',
                }}>
                    {isOpen ? '▲' : '▼'}
                </span>
            </button>

            {isOpen && (
                <div className="multiselect-dropdown" style={{
                    position: 'absolute',
                    top: '100%',
                    left: 0,
                    right: 0,
                    marginTop: '4px',
                    background: 'white',
                    border: '1px solid var(--gray-200)',
                    borderRadius: '8px',
                    boxShadow: '0 8px 24px rgba(0,0,0,0.15)',
                    zIndex: 9999,
                    maxHeight: '300px',
                    overflow: 'hidden',
                    display: 'flex',
                    flexDirection: 'column',
                }}>
                    <div style={{ padding: '8px', borderBottom: '1px solid var(--gray-100)' }}>
                        <input
                            type="text"
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            placeholder={searchPlaceholder}
                            style={{
                                width: '100%',
                                padding: '6px 10px',
                                borderRadius: '4px',
                                border: '1px solid var(--gray-200)',
                                fontSize: '0.85rem',
                                outline: 'none',
                            }}
                            onClick={(e) => e.stopPropagation()}
                        />
                    </div>

                    <div style={{ overflowY: 'auto', maxHeight: '240px' }}>
                        {showSelectAll && (
                            <label
                                style={{
                                    display: 'flex',
                                    alignItems: 'center',
                                    gap: '10px',
                                    padding: '8px 12px',
                                    cursor: 'pointer',
                                    borderBottom: '1px solid var(--gray-100)',
                                    fontWeight: '600',
                                    fontSize: '0.85rem',
                                    color: 'var(--gray-700)',
                                    background: someSelected ? 'var(--primary-light)' : 'transparent',
                                }}
                                onClick={(e) => { e.preventDefault(); toggleAll(); }}
                            >
                                <span style={{
                                    width: '18px',
                                    height: '18px',
                                    borderRadius: '4px',
                                    border: allSelected ? 'none' : '2px solid var(--gray-300)',
                                    background: allSelected ? 'var(--primary)' : (someSelected ? 'var(--primary)' : 'white'),
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    flexShrink: 0,
                                    transition: 'all 0.15s',
                                }}>
                                    {(allSelected || someSelected) && (
                                        <span style={{ color: 'white', fontSize: '12px', fontWeight: 'bold' }}>
                                            {allSelected ? '✓' : '–'}
                                        </span>
                                    )}
                                </span>
                                Seleccionar todos ({filteredItems.length})
                            </label>
                        )}

                        {filteredItems.length === 0 && (
                            <div style={{ padding: '12px', textAlign: 'center', color: 'var(--gray-400)', fontSize: '0.85rem' }}>
                                No se encontraron resultados
                            </div>
                        )}

                        {filteredItems.map(item => {
                            const isSelected = selectedIds.includes(item[valueKey]);
                            return (
                                <label
                                    key={item[valueKey]}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '10px',
                                        padding: '7px 12px',
                                        cursor: 'pointer',
                                        fontSize: '0.85rem',
                                        color: 'var(--gray-700)',
                                        background: isSelected ? 'var(--primary-light)' : 'transparent',
                                        transition: 'background 0.1s',
                                    }}
                                    onMouseEnter={(e) => e.currentTarget.style.background = isSelected ? 'var(--primary-light)' : 'var(--gray-50)'}
                                    onMouseLeave={(e) => e.currentTarget.style.background = isSelected ? 'var(--primary-light)' : 'transparent'}
                                    onClick={(e) => { e.preventDefault(); toggleItem(item[valueKey]); }}
                                >
                                    <span style={{
                                        width: '18px',
                                        height: '18px',
                                        borderRadius: '4px',
                                        border: isSelected ? 'none' : '2px solid var(--gray-300)',
                                        background: isSelected ? 'var(--primary)' : 'white',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        flexShrink: 0,
                                        transition: 'all 0.15s',
                                    }}>
                                        {isSelected && (
                                            <span style={{ color: 'white', fontSize: '12px', fontWeight: 'bold' }}>✓</span>
                                        )}
                                    </span>
                                    <span style={{ flex: 1 }}>{item[labelKey]}</span>
                                </label>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
