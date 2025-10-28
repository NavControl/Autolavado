$(function () {
    getPublicIP();
});


async function getPublicIP() {
    try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        $("#public_ip").val(data.ip);
        console.log(data.ip);
    } catch (error) {
        console.error("Error al obtener la IP pública:", error);
    }
}