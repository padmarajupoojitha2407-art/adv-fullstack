import { useState } from "react";

export default function Login({ setToken }) {
    const [rollNo, setRollNo] = useState("");
    const [password, setPassword] = useState("");
    const [message, setMessage] = useState("");

    async function handleLogin() {
        if (rollNo === "" || password === "") {
            setMessage("Please fill all fields");
            return;
        }
        const res = await fetch("http://127.0.0.1:8001/login", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                roll_no: rollNo,
                password: password
            })
        });
        const data = await res.json();
        if (data.access_token) {
            setToken(data.access_token);
        }
        // detail can be a list (422 errors), so turn it into text
        setMessage(JSON.stringify(data.detail) || "Login successful!");
    }
    return (
        <>
            <h2>Login</h2>
            <input
                placeholder="Roll number (officer: officer)"
                onChange={(e) => setRollNo(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                onChange={(e) => setPassword(e.target.value)}
            />
            <button onClick={handleLogin}>Login</button>
            <p>{message}</p>
        </>
    );
}
