let autoscrollEnabled = false;
let autoscrollInterval = null;
let autoscrollSpeed = 2;



function restartAutoscroll() {
    if (autoscrollEnabled && autoscrollInterval) {
        clearInterval(autoscrollInterval);
        autoscrollInterval = setInterval(() => {
            window.scrollBy(0, 1);
        }, 100 / autoscrollSpeed);
    }
}

function increaseAutoscrollSpeed() {
    autoscrollSpeed = Math.min(autoscrollSpeed + 0.5, 10);
    restartAutoscroll();
    const speedIndicator = document.getElementById('autoscroll-speed');
    if (speedIndicator) {
        speedIndicator.textContent = autoscrollSpeed.toFixed(1);
    }
    return autoscrollSpeed;
}

function decreaseAutoscrollSpeed() {
    autoscrollSpeed = Math.max(autoscrollSpeed - 0.5, 0.5);
    restartAutoscroll();
    const speedIndicator = document.getElementById('autoscroll-speed');
    if (speedIndicator) {
        speedIndicator.textContent = autoscrollSpeed.toFixed(1);
    }
    return autoscrollSpeed;
}

function toggleAutoscroll() {
    autoscrollEnabled = !autoscrollEnabled;

    const autoscrollBtn = document.getElementById('autoscroll-btn');
    const speedIndicator = document.getElementById('autoscroll-speed');

    if (autoscrollEnabled) {
        if (autoscrollBtn) {
            autoscrollBtn.classList.add('enabled');
        }
        if (speedIndicator) {
            speedIndicator.textContent = autoscrollSpeed.toFixed(1);
        }
        autoscrollInterval = setInterval(() => {
            window.scrollBy(0, 1);
        }, 100 / autoscrollSpeed);
    } else {
        if (autoscrollBtn) {
            autoscrollBtn.classList.remove('enabled');
        }
        if (autoscrollInterval) {
            clearInterval(autoscrollInterval);
            autoscrollInterval = null;
        }
    }

    return autoscrollEnabled;
}

const NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
const NOTE_ALIASES = {
    'Db': 'C#', 'Eb': 'D#', 'Fb': 'E', 'E#': 'F',
    'Gb': 'F#', 'Ab': 'G#', 'Bb': 'A#', 'Cb': 'B', 'B#': 'C'
};

function transposeNote(note, semitones) {
    // Normalize note (handle flats)
    const normalizedNote = NOTE_ALIASES[note] || note;
    const currentIndex = NOTE_NAMES.indexOf(normalizedNote);

    if (currentIndex === -1) {
        return note; // Invalid note, return as-is
    }

    const newIndex = (currentIndex + semitones + 12) % 12;
    return NOTE_NAMES[newIndex];
}

function transposeChord(chord, semitones) {
    const chordRegex = /([A-G][#b]?)/g;

    const rootNotes = chord.matchAll(chordRegex);

    if (!rootNotes) {
        return chord; // No valid root note found
    }

    replacements = {};
    for (const rootNote of rootNotes) {
        const transposedNote = transposeNote(rootNote[0], semitones);
        replacements[rootNote[0]] = transposedNote;
    }
    return chord.replace(
        new RegExp(Object.keys(replacements).join("|"),"gi"),
        matched => replacements[matched] || matched);
}

function transposeSong(divId, semitones) {
    const div = document.getElementById(divId);

    if (!div) {
        return; // Div not found
    }

    const chordSpans = div.querySelectorAll('span.chord');

    chordSpans.forEach(span => {
        const originalChord = span.textContent;
        const transposedChord = transposeChord(originalChord, semitones);
        span.textContent = transposedChord;
    });
}

