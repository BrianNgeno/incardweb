// InCAD Website JS
document.addEventListener('DOMContentLoaded',()=>{
  // Mobile nav
  const toggle=document.querySelector('.nav-toggle');
  const links=document.querySelector('.nav-links');
  if(toggle){toggle.addEventListener('click',()=>links.classList.toggle('open'));}

  // Active link
  const path=location.pathname.split('/').pop()||'index.html';
  document.querySelectorAll('.nav-links a').forEach(a=>{
    if(a.getAttribute('href')===path)a.classList.add('active');
  });

  // Year
  const y=document.getElementById('year');if(y)y.textContent=new Date().getFullYear();


});

// Gallery / Carousel
document.addEventListener('DOMContentLoaded',()=>{
  const items = Array.from(document.querySelectorAll('.gallery-item'));
  const modal = document.getElementById('gallery-modal');
  if(!modal || items.length===0) return;
  const modalPhoto = modal.querySelector('.modal-photo');
  const modalTitle = modal.querySelector('.modal-title');
  const modalDesc = modal.querySelector('.modal-desc');
  const closeBtn = modal.querySelector('.modal-close');
  const prevBtn = modal.querySelector('.modal-nav.prev');
  const nextBtn = modal.querySelector('.modal-nav.next');
  const overlay = modal.querySelector('.modal-overlay');
  let current = 0;

  function showIndex(i){
    const idx = (i + items.length) % items.length;
    current = idx;
    const it = items[idx];
    const full = it.getAttribute('data-full') || it.querySelector('img').src;
    const name = it.getAttribute('data-name') || '';
    const desc = it.getAttribute('data-desc') || '';
    modalPhoto.src = full;
    modalPhoto.alt = name;
    modalTitle.textContent = name;
    modalDesc.textContent = desc;
  }

  function openModal(i){
    showIndex(i);
    modal.setAttribute('aria-hidden','false');
    document.body.style.overflow = 'hidden';
    // focus close for accessibility
    closeBtn.focus();
  }
  function closeModal(){
    modal.setAttribute('aria-hidden','true');
    document.body.style.overflow = '';
  }

  items.forEach((el, idx)=>{
    el.addEventListener('click',()=>openModal(idx));
    el.addEventListener('keydown',(e)=>{ if(e.key==='Enter' || e.key===' ') { e.preventDefault(); openModal(idx); } });
  });

  closeBtn.addEventListener('click',closeModal);
  overlay.addEventListener('click',closeModal);
  prevBtn.addEventListener('click',()=>showIndex(current-1));
  nextBtn.addEventListener('click',()=>showIndex(current+1));

  document.addEventListener('keydown',(e)=>{
    if(modal.getAttribute('aria-hidden')==='false'){
      if(e.key==='Escape') closeModal();
      if(e.key==='ArrowLeft') showIndex(current-1);
      if(e.key==='ArrowRight') showIndex(current+1);
    }
  });
});

document.addEventListener('DOMContentLoaded',()=>{
  const track = document.querySelector('.upcoming-programs .slider-track');
  const slides = track ? Array.from(track.children) : [];
  const prev = document.querySelector('.slider-control.prev');
  const next = document.querySelector('.slider-control.next');
  if(!track || slides.length === 0 || !prev || !next) return;
  let currentIndex = 0;

  function updateSlider(index){
    currentIndex = (index + slides.length) % slides.length;
    track.style.transform = `translateX(-${currentIndex * 100}%)`;
  }

  prev.addEventListener('click',()=>updateSlider(currentIndex - 1));
  next.addEventListener('click',()=>updateSlider(currentIndex + 1));

  let startX = 0;
  let isDragging = false;

  track.addEventListener('pointerdown',(event)=>{
    isDragging = true;
    startX = event.clientX;
    track.style.transition = 'none';
  });

  track.addEventListener('pointermove',(event)=>{
    if(!isDragging) return;
    const delta = event.clientX - startX;
    track.style.transform = `translateX(calc(-${currentIndex * 100}% + ${delta}px))`;
  });

  track.addEventListener('pointerup',event=>{
    if(!isDragging) return;
    isDragging = false;
    const delta = event.clientX - startX;
    track.style.transition = '';
    if(delta < -60) updateSlider(currentIndex + 1);
    else if(delta > 60) updateSlider(currentIndex - 1);
    else updateSlider(currentIndex);
  });

  track.addEventListener('pointerleave',()=>{
    if(isDragging){
      isDragging = false;
      updateSlider(currentIndex);
    }
  });
});
