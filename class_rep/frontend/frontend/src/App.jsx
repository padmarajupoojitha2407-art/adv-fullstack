import { useState } from "react";
import Login from "./components/Login.jsx";
import Register from "./components/Register.jsx";
import Election from "./components/Election.jsx";
import Nominate from "./components/Nominate.jsx";
import Vote from "./components/Vote.jsx";
import Officer from "./components/Officer.jsx";
import "./App.css";

function App() {
    // the token from Login is kept here and given to every other component
    const [token, setToken] = useState("");

    return (
        <div className="auth-container">
            <div className="auth-box">
                <Register />
            </div>

            <div className="auth-box">
                <Login setToken={setToken} />
            </div>

            <div className="auth-box">
                <Election token={token} />
            </div>

            <div className="auth-box">
                <Nominate token={token} />
            </div>

            <div className="auth-box">
                <Vote token={token} />
            </div>

            <div className="auth-box">
                <Officer token={token} />
            </div>
        </div>
    );
}

export default App;
