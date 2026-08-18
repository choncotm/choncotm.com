const translations = {
  fr: {
    "nav.home": "Accueil",
    "nav.projects": "Projets",
    "nav.contact": "Contact",
    "hero.tagline": "Développeur indépendant — cybersécurité, services, logiciels, petits outils, bots et sites, faits avec soin.",
    "projects.heading": "Projets",
    "projects.aptDesc": "Bot Telegram qui surveille le prix de produits Amazon et prévient en cas de changement.",
    "projects.siteDesc": "Le site sur lequel tu te trouves : ma vitrine, mon portfolio, mon image de marque.",
    "projects.openBot": "Ouvrir le bot",
    "projects.sourceCode": "Code source",
    "projects.private": "(privé)",
    "projects.public": "(public)",
    "projects.privacyPolicy": "Politique de confidentialité",
    "contact.heading": "Contact",
  },
  en: {
    "nav.home": "Home",
    "nav.projects": "Projects",
    "nav.contact": "Contact",
    "hero.tagline": "Independent developer — cybersecurity, services, software, small tools, bots and websites, made with care.",
    "projects.heading": "Projects",
    "projects.aptDesc": "Telegram bot that tracks Amazon product prices and notifies you when they change.",
    "projects.siteDesc": "The site you're on right now: my showcase, my portfolio, my personal brand.",
    "projects.openBot": "Open the bot",
    "projects.sourceCode": "Source code",
    "projects.private": "(private)",
    "projects.public": "(public)",
    "projects.privacyPolicy": "Privacy policy",
    "contact.heading": "Contact",
  },
  pt: {
    "nav.home": "Início",
    "nav.projects": "Projetos",
    "nav.contact": "Contacto",
    "hero.tagline": "Programador independente — cibersegurança, serviços, software, pequenas ferramentas, bots e sites, feitos com cuidado.",
    "projects.heading": "Projetos",
    "projects.aptDesc": "Bot do Telegram que acompanha o preço de produtos da Amazon e avisa quando mudam.",
    "projects.siteDesc": "O site em que estás agora: a minha vitrine, o meu portfólio, a minha imagem de marca.",
    "projects.openBot": "Abrir o bot",
    "projects.sourceCode": "Código-fonte",
    "projects.private": "(privado)",
    "projects.public": "(público)",
    "projects.privacyPolicy": "Política de privacidade",
    "contact.heading": "Contacto",
  },
  es: {
    "nav.home": "Inicio",
    "nav.projects": "Proyectos",
    "nav.contact": "Contacto",
    "hero.tagline": "Desarrollador independiente — ciberseguridad, servicios, software, pequeñas herramientas, bots y sitios, hechos con cuidado.",
    "projects.heading": "Proyectos",
    "projects.aptDesc": "Bot de Telegram que vigila el precio de productos de Amazon y avisa cuando cambian.",
    "projects.siteDesc": "El sitio en el que estás ahora: mi escaparate, mi portafolio, mi imagen de marca.",
    "projects.openBot": "Abrir el bot",
    "projects.sourceCode": "Código fuente",
    "projects.private": "(privado)",
    "projects.public": "(público)",
    "projects.privacyPolicy": "Política de privacidad",
    "contact.heading": "Contacto",
  },
  ru: {
    "nav.home": "Главная",
    "nav.projects": "Проекты",
    "nav.contact": "Контакты",
    "hero.tagline": "Независимый разработчик — кибербезопасность, услуги, программное обеспечение, небольшие инструменты, боты и сайты, сделанные с заботой.",
    "projects.heading": "Проекты",
    "projects.aptDesc": "Телеграм-бот, который отслеживает цены на товары Amazon и уведомляет об изменениях.",
    "projects.siteDesc": "Сайт, на котором ты сейчас находишься: моя витрина, моё портфолио, мой личный бренд.",
    "projects.openBot": "Открыть бота",
    "projects.sourceCode": "Исходный код",
    "projects.private": "(приватный)",
    "projects.public": "(публичный)",
    "projects.privacyPolicy": "Политика конфиденциальности",
    "contact.heading": "Контакты",
  },
  de: {
    "nav.home": "Start",
    "nav.projects": "Projekte",
    "nav.contact": "Kontakt",
    "hero.tagline": "Unabhängiger Entwickler — Cybersicherheit, Dienstleistungen, Software, kleine Tools, Bots und Websites, mit Sorgfalt gemacht.",
    "projects.heading": "Projekte",
    "projects.aptDesc": "Telegram-Bot, der Amazon-Produktpreise überwacht und bei Änderungen benachrichtigt.",
    "projects.siteDesc": "Die Seite, auf der du gerade bist: mein Schaufenster, mein Portfolio, meine Marke.",
    "projects.openBot": "Bot öffnen",
    "projects.sourceCode": "Quellcode",
    "projects.private": "(privat)",
    "projects.public": "(öffentlich)",
    "projects.privacyPolicy": "Datenschutzerklärung",
    "contact.heading": "Kontakt",
  },
};

function applyLanguage(lang) {
  const dict = translations[lang] ? lang : "fr";
  const strings = translations[dict];

  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const key = el.getAttribute("data-i18n");
    if (strings[key]) el.textContent = strings[key];
  });

  document.documentElement.lang = dict;
  localStorage.setItem("lang", dict);

  const select = document.getElementById("lang-select");
  if (select) select.value = dict;
}

const storedLang = localStorage.getItem("lang");
const browserLang = (navigator.language || "fr").slice(0, 2);
applyLanguage(storedLang || browserLang);

document.getElementById("lang-select")?.addEventListener("change", (event) => {
  applyLanguage(event.target.value);
});
