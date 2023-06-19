// All edit types
export const EDIT_TYPES = [
    'deletion',
    'insertion',
    'substitution',
    'split',
    'reorder',
    'structure'
]

// Underlying edit span types
export const CONSTITUENT_TYPES = [
    'deletion',
    'insertion',
    'substitution',
    'reorder'
]

// Edit types that are connected from input to output
export const CONNECTED_TYPES = [
    'split',
    'substitution',
    'reorder',
    'structure'
]

export const EMPTY_ANNOTATION = Object.fromEntries(EDIT_TYPES.map(t => [t, {}]));
export const EMPTY_CONSTITUENT_TYPES = Object.fromEntries(CONSTITUENT_TYPES.map(t => [t, {}]));
export const EMPTY_CONNECTED_TYPES = Object.fromEntries(CONNECTED_TYPES.map(t => [t, {}]));

export const DOWNLOAD_FILE_NAME = "annotations.json";
