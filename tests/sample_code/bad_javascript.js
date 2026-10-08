function runQuery(userInput) {
    // Hard-coded secret token
    const token = "ghp_secret_access_token_1234567890";

    // Dangerous eval execution
    eval("var x = " + userInput);

    // Unhandled promise
    fetch("/api/data").then(res => res.json());

    return token;
}
