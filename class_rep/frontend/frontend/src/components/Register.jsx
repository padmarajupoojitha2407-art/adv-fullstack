import { useState } from "react";

export default function Register() {
    const [rollNo, setRollNo] = useState("");
    const [password, setPassword] = useState("");
    const [userType, setUserType] = useState("");
    const [message, setMessage] = useState("");

    async function handleRegister() {
        if (rollNo === "" || password === "" || userType === "") {
            setMessage("Please fill all fields");
            return;
        }
        const res = await fetch("http://127.0.0.1:8001/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                roll_no: rollNo,
                password: password,
                user_type: userType
            })
        });
        const data = await res.json();
        // detail can be a list (422 errors), so turn it into text
        setMessage(data.message || JSON.stringify(data.detail));
    }
    return (
        <>
            <h2>Register</h2>
            <input
                placeholder="Roll number"
                onChange={(e) => setRollNo(e.target.value)}
            />
            <input
                type="password"
                placeholder="Password"
                onChange={(e) => setPassword(e.target.value)}
            />
            <input
                placeholder="student or candidate"
                onChange={(e) => setUserType(e.target.value)}
            />
            <button onClick={handleRegister}>Register</button>
            <p>{message}</p>
        </>
    );
}
