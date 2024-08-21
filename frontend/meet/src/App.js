import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './pages/Layout';
import Call from './pages/Call';
import Home from './pages/Home';


function App() {
    return (
        <BrowserRouter>
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Home />} />
                    <Route path="call" element={<Call />} />
                </Route>
            </Routes>
        </BrowserRouter>
    );
}

export default App;