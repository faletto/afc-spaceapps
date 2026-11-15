/** Entry point: mounts <App /> and loads the global theme. */
import { createRoot } from 'react-dom/client';
import './theme.css';
import { App } from './App';
createRoot(document.getElementById('root')!).render(<App />);
