async function postJSON(route, data){
  let response = await fetch(route, {
      method: "POST",
      headers: {
        "Content-Type": "application/json;charset=UTF-8", //обязательный заголовок для формата json
      },
      body: JSON.stringify(data),
    });
    return await response.json()
}

document.addEventListener('click', function(e){
if(e.target.classList.contains("edit")){
        postJSON("/getLinkName", {id: e.target.dataset.id}).then(function(nicname){
            postJSON("/gethostname", '').then(function(hostName){
              let nicnamered = nicname.replace(hostName,'')
              console.log(hostName)
                document.querySelector("body").insertAdjacentHTML("beforeend", `
                <div class="modallll-wrapper">
                    <div class="modallll ShowRewiewModal">
                        <button id="closeModal" class="close">❌</button>
                        <div>
                        <form action="/changeLinkNickName" method="post">


                            <h2>Изменить псевдоним</h2>
                            <div class="row g-3 align-items-center">
                            <div class="col-auto">
                            <label for="nickName" class="col-form-label">${hostName} </label>
                            </div>
                            <div class="col-auto">
                            <input class="form-control mb-2" type="text" id="nickName" name="nickName" value=${nicnamered}>
                            </div>
                            </div>
                            <div class="row g-3 align-items-center">
                            <div class="col-auto">
                            <button class="changeLinkConfirm btn btn-warning" name="id" value='${e.target.dataset.id}'>Подтвердить изменение</button>
                            </div>
                            <div class="col-auto">
                            <button class="changeLinkConfirm btn btn-warning" name="random" value='${e.target.dataset.id}'>Случайный псевдоним</button>
                            </div>
                        </div>
                        </form>
                        <h2 class="mt-2 mb-2">Изменить Доступ</h2>
                        <form action="/changeLinkStatus" method="post">
                        <select class="form-select mb-2 mt-2 col-4" aria-label="Default select example" name="lvl">
                          <option value="1">Публичная</option>
                          <option value="2">Общего доступа</option>
                          <option value="3">Приватная</option>
                        </select>

                        <button class="changeLinkConfirm btn btn-warning" name="id" value='${e.target.dataset.id}'>Подтвердить изменение</button>
                        </form>
                        </div>
                    </div>
                  </div>
                `)
                modal = document.querySelector(".modallll-wrapper")
                modal.addEventListener("click", function(e){
                    if(e.target == e.currentTarget){
                      modal.remove()
                    }
                  })
                  document.addEventListener("keyup", function(e){
                    console.log(e.key)
                    if(e.key == "Escape"){
                      modal.remove()
                    }
                  })
                  document.querySelector('#closeModal').addEventListener("click", function(e){
                      modal.remove()
                  })
            })
        })
    }
})