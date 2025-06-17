$(function () {
  document
    .getElementById("support-msg-form")
    .addEventListener("submit", function (e) {
      e.preventDefault();
      const content = document.getElementById("messageContent").value;
      $("#submited-msg").hide();
      $("#support-msg-form").hide();
      $("#support-msg-loader-container").css({ display: "flex" });
      $("#support-msg-loader-container").show();
      fetch("/api/support_msg", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCookie("csrftoken"), // CSRF対策
        },
        body: JSON.stringify({ msg: content }),
      })
        .then((response) => {
          if (!response.ok) {
            // 200番台以外はエラー扱い
            return response.json().then((errData) => {
              throw new Error(JSON.stringify(errData));
            });
          }
          return response.json();
        })
        .then((data) => {
          document.getElementById("messageContent").value = "";
          showSentMsg(data.message, "green");
        })
        .catch((error) => {
          showSentMsg(JSON.parse(error.message).message, "red");
        });
    });

  function showSentMsg(msg, color) {
    $("#support-msg-loader-container").hide();
    $("#support-msg-form").show();
    $("#submited-msg").text(msg);
    $("#submited-msg").css("color", color);
    $("#submited-msg").fadeIn();
  }

  // CSRFトークン取得関数
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // 非同期関数を定義
  async function fetchData() {
    try {
      const response = await fetch("./api/support_msg");
      if (!response.ok) {
        throw new Error("ネットワークエラー");
      }
      const data = await response.json();
      console.log(data);

      for (const msg of data["messages"]) {
        const ul = document.querySelector("ul.slider"); // ul.sliderを取得
        const newLi = document.createElement("li"); // 新しいli要素を作成
        newLi.textContent = msg;
        ul.appendChild(newLi); // ulにliを追加
      }
      $(".slider").slick({
        // オプションを記述
      });
      setInterval(function () {
        $(".slider").slick("slickNext");
      }, 1500);
      $(".slick-arrow").hide();
      $("#support-msg-area").fadeIn();
    } catch (error) {}
  }

  fetchData();
});
