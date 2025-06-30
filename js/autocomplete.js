
    localStorage.removeItem("buffer_length")
    const input = document.getElementById("staticTitle");
    const ghost = document.getElementById("ghostSuggestion");
    input.addEventListener("input", async () => {
      const text = input.value;
      ghost.innerText = "";
      bufferLength = ""
      
      if (text.length > 3) {
        try {

          $.ajax({
              url: "http://127.0.0.1:5000/autocomplete",
              headers: {
                  "token": localStorage.getItem("user_token")
              },
              method: 'POST',
              contentType: 'application/json',
              data: JSON.stringify({ prefix: text }),
              success: function(data) {
                // const data = response.json();
                if (data.suggestion && data.suggestion !== text) {
                  const suggestion = data.suggestion;
                  const remaining = suggestion.slice(text.length);
                  ghost.innerText = bufferLength + text + remaining;
                }
              },
              error: function(jqXHR, textStatus, errorThrown) {
                console.error("Error in autocomplete:", textStatus, errorThrown);
              },
          })          
        } catch (err) {
          console.error("AI error:", err);
        }
      }
    });

    input.addEventListener("keydown", (e) => {
      if (e.key === "Tab" && ghost.innerText) {
        e.preventDefault();
        input.value = ghost.innerText;
        ghost.innerText = "";
        localStorage.removeItem("buffer_length")
      }
    });

    function createBuffer(l){
      let whiteStr = "";
      for (let i = 0; i < l; i++) {
        whiteStr += " ";
      }
      return whiteStr;
    }
  