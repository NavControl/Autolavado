$('.input_number').on('input', function () {
  this.value = this.value.replace(/[^0-9]/g, '');
});

$(".input_identifier").keypress(function (evt) {
  var code = (evt.which) ? evt.which : evt.keyCode;
  return ((code >= 65 && code <= 90) || (code >= 97 && code <= 122) || code == 95) ? true : false;
});

$(".input_general").keypress(function (evt) {
  var code = (evt.which) ? evt.which : evt.keyCode;
  return ((code >= 65 && code <= 90) || (code >= 97 && code <= 122) || code == 95) ? true : false;
});


function zfill(number, width) {
  var numberOutput = Math.abs(number);
  var length = number.toString().length;
  var zero = "0";
  if (width <= length) {
    if (number < 0) {
      return ("-" + numberOutput.toString());
    } else {
      return numberOutput.toString();
    }
  } else {
    if (number < 0) {
      return ("-" + (zero.repeat(width - length)) + numberOutput.toString());
    } else {
      return ((zero.repeat(width - length)) + numberOutput.toString());
    }
  }
}

function messages(title = "Mensaje", msg, type = "info", time = 3000) {
  var icono = "", color = "";
  if (type == "success") {
    icono = "fas fa-check-circle";
    color = "green";
  } else if (type == "danger" || type == "error") {
    icono = "fas fa-exclamation-triangle";
    color = "red";
  } else if (type == "warning") {
    icono = "fas fa-exclamation-triangle";
    color = "orange";
  } else if (type == "info") {
    icono = "fas fa-info-circle";
    color = "blue";
  }
  var delay = 'okay|' + time;
  $.alert({
    title: title,
    content: msg,
    type: color,
    theme: 'modern',
    icon: icono,
    animation: 'scaleY',
    closeAnimation: 'scaleY',
    animateFromElement: false,
    closeIcon: true,
    animation: 'scale',
    autoClose: delay,
    buttons: {
      okay: {
        keys: ['enter'],
        text: 'Aceptar',
        btnClass: 'btn-' + color,
      },
    },
  });
}

function settings_input() {
  $('input').attr('autocomplete', 'off').attr("placeholder", "Escribe aquí...");
  // $('form').find("input[type=text], input[type=password], input[type=email]").each(function (ev) {
  //   if (!$(this).val()) {
  //     $(this).attr("placeholder", "Escribe aquí...");
  //   }
  // });
}

// function formato_fecha(fecha, tipo_fecha = "NORMAL") {
//   if (!Boolean(fecha)) {
//     return "";
//   } else {
//     fecha = fecha.replace('-', '/').replace('-', '/');
//     let dias = ['domungo', 'lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sábado'];
//     let meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'];
//     let separa_fecha = fecha.split('.');
//     const date = new Date(separa_fecha[0]);

//     let DiaSemanaTexto = dias[date.getDay()];
//     let DiaMes = zfill(date.getDate(), 2);
//     let MesTexto = meses[date.getMonth()];
//     let Anio = date.getFullYear();
//     let Horas = zfill(date.getHours(), 2);
//     let Minutos = zfill(date.getMinutes(), 2);
//     let Segundos = zfill(date.getSeconds(), 2);


//     let fecha_nuevo = `${DiaSemanaTexto} ${DiaMes} de ${MesTexto} de ${Anio} ${Horas}:${Minutos}:${Segundos}`;
//     if (tipo_fecha == "FN") {
//       fecha_nuevo = `${date.getDate()} de ${meses[date.getMonth()]} de ${date.getFullYear()}`;
//     } else if (tipo_fecha == "HORA") {
//       fecha_nuevo = `${zfill(date.getHours(), 2)}:${zfill(date.getMinutes(), 2)}:${zfill(date.getSeconds(), 2)}`;
//     } else if (tipo_fecha == "HORA_CORTA") {
//       fecha_nuevo = `${zfill(date.getHours(), 2)}:${zfill(date.getMinutes(), 2)}`;
//     } else if (tipo_fecha == 'F_BD') {
//       fecha_nuevo = `${date.getFullYear()}-${date.getMonth() + 1}-${date.getDate()}`;
//     }
//     return fecha_nuevo;
//   }
// }

function formato_miles(cantidad) {
  let canti = Boolean(cantidad) ? cantidad : 0;
  var formatNumber = {
    separador: ",", // separador para los miles
    sepDecimal: ".", // separador para los decimales
    formatear: function (num) {
      num += "";
      var splitStr = num.split(".");
      var splitLeft = splitStr[0];
      var splitRight = splitStr.length > 1 ? this.sepDecimal + splitStr[1] : "";
      var regx = /(\d+)(\d{3})/;
      while (regx.test(splitLeft)) {
        splitLeft = splitLeft.replace(regx, "$1" + this.separador + "$2");
      }
      return this.simbol + splitLeft + splitRight;
    },
    new: function (num, simbol) {
      this.simbol = simbol || "";
      return this.formatear(num);
    }
  };
  return formatNumber.new(canti + ".00", "$ ");
}

function format_double(evt, input) {
  var key = window.Event ? evt.which : evt.keyCode;
  var chark = String.fromCharCode(key);
  var tempValue = input.value + chark;
  if (key >= 48 && key <= 57) {
    if (filter(tempValue) === false) {
      return false;
    } else {
      return true;
    }
  } else {
    if (key == 8 || key == 13 || key == 0) {
      return true;
    } else if (key == 46) {
      if (filter(tempValue) === false) {
        return false;
      } else {
        return true;
      }
    } else {
      return false;
    }
  }
}

function filter(__val__) {
  var preg = /^([0-9]+\.?[0-9]{0,2})$/;
  if (preg.test(__val__) === true) {
    return true;
  } else {
    return false;
  }
}

function alerts(title, msj, type = 'info', time = 5000) {
  let icon = type == 'success' ? 'check' : (type == 'danger' ? 'times' : (type == 'info' ? 'info' : (type == 'warning' ? 'exclamation-triangle' : '')));
  let color = type == 'success' ? '#28A745' : (type == 'danger' ? '#DC3545' : (type == 'info' ? '#17A2B8' : (type == 'warning' ? '#FFC107' : '')));
  iziToast.show({
    title: title,
    message: msj,
    position: 'bottomRight',
    icon: 'fa fa-' + icon,
    backgroundColor: color,
    messageColor: '#FFFFFF',
    titleColor: "#FFFFFF",
    iconColor: "#FFFFFF",
    maxWidth: '500px',
    layout: 2,
    timeout: time,
  });
}

function alerts_notify(title, msj, type = 'info') {
  let icon = type == 'success' ? 'check' : (type == 'danger' ? 'times' : (type == 'info' ? 'info' : (type == 'warning' ? 'exclamation-triangle' : '')));
  let color = type == 'success' ? '#28A745' : (type == 'danger' ? '#DC3545' : (type == 'info' ? '#17A2B8' : (type == 'warning' ? '#FFC107' : '')));
  iziToast.show({
    title: title,
    message: msj,
    position: 'bottomRight',
    icon: 'fa fa-' + icon,
    backgroundColor: color,
    messageColor: '#FFFFFF',
    titleColor: "#FFFFFF",
    iconColor: "#FFFFFF",
    maxWidth: '500px',
    layout: 2,
    timeout: false,
    closeOnClick: true,
  });
}

function getDatesInRange(startDate, endDate) {
  const dates = [];
  const currentDate = new Date(startDate);

  while (currentDate <= endDate) {
    currentDate.setDate(currentDate.getDate() + 1);
    dates.push(new Date(currentDate));
  }

  return dates;
}

function formato_mil(numero) {
  // Usa toLocaleString con 'es-MX' como idioma para formatear el número
  return numero.toLocaleString('es-MX');
}

function mostrarConfirmacion(mensaje) {
  return new Promise((resolve, reject) => {
    $.confirm({
      title: '¡CONFIRMAR!',
      content: mensaje,
      theme: 'modern',
      type: 'orange',
      icon: 'fas fa-exclamation-triangle',
      animation: 'scaleY',
      closeAnimation: 'scaleY',
      animateFromElement: false,
      closeIcon: true,
      animation: 'scale',
      autoClose: 'cancel|8000',
      buttons: {
        confirm: {
          text: 'Aceptar',
          btnClass: 'btn-green',
          action: function () {
            resolve(true); // Resolvemos la promesa con true
          }
        },
        cancel: {
          text: 'Cancelar',
          btnClass: 'btn-red',
          action: function () {
            resolve(false); // Resolvemos la promesa con false
          }
        }
      },
      onClose: function () {
        resolve(false); // Si cierran la ventana, resolvemos con false
      }
    });
  });
}

function formato_fecha(fecha_rec, tipo = "FN") {
  if (Boolean(fecha_rec)) {
    const fecha = new Date(fecha_rec);
    const dia = fecha.getUTCDate();
    const mes = fecha.toLocaleString('es-ES', { month: 'long', timeZone: 'UTC' });
    const anio = fecha.getUTCFullYear();
    const hora = fecha.getUTCHours().toString().padStart(2, '0');
    const minutos = fecha.getUTCMinutes().toString().padStart(2, '0');
    const segundos = fecha.getUTCSeconds().toString().padStart(2, '0');
    let fecha_ret = "";
    if (tipo === "FN") {
      fecha_ret = `${dia} de ${mes} de ${anio}`;
    } else if (tipo === "FULL") {
      fecha_ret = `${dia} de ${mes} de ${anio} ${hora}:${minutos}:${segundos}`;
    }
    return fecha_ret;
  } else {
    return "";
  }
}

function validarEmail(email) {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
}
