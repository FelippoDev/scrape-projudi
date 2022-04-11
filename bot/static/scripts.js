$(document).ready(() => {
    $('button').click(e => {
      e.preventDefault();
      // URL AQUI
      let url = 'http://127.0.0.1:80' // caminho completo

      $.ajax({
        method: 'POST',
        url: url,
        data: {
          user: $("#user").val(),
          pwd: $("#pwd").val(),
          token: $('#token').val() // SE QUISER ALTERAR O NOME QUE RECEBE NO POST, muda o que tá antes dos dois pontos
        },
        beforeSend: () => {
          $("#load").toggleClass("d-none");
        },
        success: () => {
          $("#load").toggleClass("d-none");
          alert("Scrap terminado com sucesso!")
        },
        error: (e, a, j) => {
          $("#load").toggleClass("d-none");
          alert("Ocorreu um erro!");
          console.log(e, a, j);
        }
      })
    });
  });