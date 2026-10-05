/**
 * Cash Back Kart — Luxury Editorial Experience Logic
 * Matches the interactive feel, category filtering, stepping tabs, and reward calculations.
 */

document.addEventListener('DOMContentLoaded', () => {
  // Elements
  const header = document.getElementById('siteHeader');
  const mobileToggle = document.getElementById('mobileToggle');
  const navMenu = document.getElementById('navMenu');
  const navLinks = document.querySelectorAll('.nav-link');
  const toast = document.getElementById('toast');

  // 1. Sticky Minimalist Navbar with Blur on Scroll
  const handleScroll = () => {
    if (window.scrollY > 30) {
      header.classList.add('is-scrolled');
    } else {
      header.classList.remove('is-scrolled');
    }
  };

  window.addEventListener('scroll', handleScroll, { passive: true });
  handleScroll();

  // 2. Mobile Menu Toggle
  if (mobileToggle && navMenu) {
    mobileToggle.addEventListener('click', () => {
      const isOpen = navMenu.classList.toggle('is-open');
      mobileToggle.setAttribute('aria-expanded', isOpen);
    });

    navLinks.forEach(link => {
      link.addEventListener('click', () => {
        navMenu.classList.remove('is-open');
        mobileToggle.setAttribute('aria-expanded', 'false');
      });
    });
  }

  // 3. Four Stepping Stones Tab & Image Switcher (Reference Image 2 Top)
  const steppingTabs = document.querySelectorAll('.stepping-tab');
  const steppingDisplayImg = document.getElementById('steppingDisplayImg');

  const steppingImages = {
    '1': 'https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=900&q=80',
    '2': 'https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=900&q=80',
    '3': 'https://images.unsplash.com/photo-1522202176988-66273c2fd55f?auto=format&fit=crop&w=900&q=80',
    '4': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=900&q=80'
  };

  steppingTabs.forEach(tab => {
    tab.addEventListener('click', () => {
      steppingTabs.forEach(t => t.classList.remove('is-active'));
      tab.classList.add('is-active');

      const stepId = tab.getAttribute('data-step');
      if (steppingImages[stepId] && steppingDisplayImg) {
        steppingDisplayImg.style.opacity = '0.2';
        setTimeout(() => {
          steppingDisplayImg.src = steppingImages[stepId];
          steppingDisplayImg.style.opacity = '1';
        }, 180);
      }
    });

    tab.addEventListener('keydown', (e) => {
      if (e.key === 'Enter' || e.key === ' ') {
        e.preventDefault();
        tab.click();
      }
    });
  });

  // 4. Store Discovery Category Filters
  const filterPills = document.querySelectorAll('.filter-pill');
  const storeCards = document.querySelectorAll('.store-editorial-card');

  filterPills.forEach(pill => {
    pill.addEventListener('click', () => {
      filterPills.forEach(p => p.classList.remove('is-active'));
      pill.classList.add('is-active');

      const category = pill.getAttribute('data-cat');

      storeCards.forEach(card => {
        const cardCategory = card.getAttribute('data-category');
        if (category === 'all' || cardCategory === category) {
          card.style.display = 'flex';
          setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
          }, 50);
        } else {
          card.style.opacity = '0';
          card.style.transform = 'translateY(10px)';
          setTimeout(() => {
            card.style.display = 'none';
          }, 200);
        }
      });
    });
  });

  // 5. Interactive Coin Rewards Calculator
  const spendSlider = document.getElementById('spendSlider');
  const spendDisplay = document.getElementById('spendDisplay');
  const storeChips = document.querySelectorAll('.store-chip');
  const annualCoinsDisplay = document.getElementById('annualCoinsDisplay');
  const annualCashDisplay = document.getElementById('annualCashDisplay');

  let currentRate = 0.10; // 10% average rate

  const formatNumberINR = (num) => {
    return new Intl.NumberFormat('en-IN').format(num);
  };

  const updateCalculator = () => {
    if (!spendSlider) return;
    const monthlySpend = parseInt(spendSlider.value, 10);
    
    if (spendDisplay) {
      spendDisplay.textContent = `₹${formatNumberINR(monthlySpend)} / mo`;
    }

    const annualSpend = monthlySpend * 12;
    const annualCashValue = Math.round(annualSpend * currentRate);
    // Fixed benchmark: 10 CBK Coins = 1 INR
    const annualCoins = annualCashValue * 10;

    if (annualCoinsDisplay) {
      annualCoinsDisplay.textContent = formatNumberINR(annualCoins);
    }
    if (annualCashDisplay) {
      annualCashDisplay.textContent = `≈ ₹${formatNumberINR(annualCashValue)} INR Direct Bank Transfer`;
    }
  };

  if (spendSlider) {
    spendSlider.addEventListener('input', updateCalculator);
  }

  storeChips.forEach(chip => {
    chip.addEventListener('click', () => {
      storeChips.forEach(c => c.classList.remove('is-selected'));
      chip.classList.add('is-selected');
      currentRate = parseFloat(chip.getAttribute('data-rate')) || 0.10;
      updateCalculator();
    });
  });

  // Initial calculation
  updateCalculator();

  // 6. Toast Notification Utility
  const showToast = (message, duration = 4500) => {
    if (!toast) return;
    toast.textContent = message;
    toast.classList.add('show');
    setTimeout(() => {
      toast.classList.remove('show');
    }, duration);
  };

  // 7. Minimalist Pill Form Sign-Up Handling
  const signupForm = document.getElementById('signupForm');
  const userEmail = document.getElementById('userEmail');
  const formFeedback = document.getElementById('formFeedback');
  const signupSubmitBtn = document.getElementById('signupSubmitBtn');

  if (signupForm && userEmail) {
    signupForm.addEventListener('submit', (e) => {
      e.preventDefault();
      const email = userEmail.value.trim();

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        if (formFeedback) {
          formFeedback.textContent = 'Please provide a valid email address.';
          formFeedback.style.color = '#C93B2B';
        }
        return;
      }

      // Simulate registration
      signupSubmitBtn.disabled = true;
      signupSubmitBtn.textContent = 'JOINING...';

      setTimeout(() => {
        userEmail.value = '';
        signupSubmitBtn.disabled = false;
        signupSubmitBtn.textContent = 'SIGNED UP';

        if (formFeedback) {
          formFeedback.textContent = '✓ You are on the private access list. 500 Welcome Coins reserved.';
          formFeedback.style.color = '#2D7D46';
        }

        showToast('✓ Welcome to Cash Back Kart! Confirmation link sent to your email.');

        setTimeout(() => {
          signupSubmitBtn.textContent = 'SIGN UP';
          if (formFeedback) formFeedback.textContent = '';
        }, 4000);
      }, 600);
    });
  }

  // 8. Legal Modals
  const legalTriggers = document.querySelectorAll('.legal-trigger');
  const legalModal = document.getElementById('legalModal');
  const modalTitle = document.getElementById('modalTitle');
  const modalBody = document.getElementById('modalBody');
  const modalClose = document.getElementById('modalClose');
  const modalDismiss = document.getElementById('modalDismiss');

  const modalContents = {
    privacy: {
      title: 'Privacy Policy',
      html: `
        <p><strong>Effective Date:</strong> January 2026</p>
        <p>Cash Back Kart ("we", "our") is dedicated to safeguarding consumer privacy. We gather minimal shopping telemetry solely required to verify and credit cashback on partner platforms like Amazon, Flipkart, Myntra, and Meesho.</p>
        <p>We never sell your personal data or store sensitive banking passwords. For queries, reach us at <strong>Cashbackkart.official@gmail.com</strong>.</p>
      `
    },
    terms: {
      title: 'Terms of Service',
      html: `
        <p><strong>1. Acceptance:</strong> By accessing Cash Back Kart, you agree to these terms of service.</p>
        <p><strong>2. Coin Accrual:</strong> Cashback coins are confirmed once merchant return windows close (typically 30–60 days). Confirmed coins carry no expiration date for active accounts.</p>
        <p><strong>3. Redemptions:</strong> Payouts to UPI IDs and Indian bank accounts are executed without transaction processing deductions.</p>
      `
    },
    coins: {
      title: 'Coin Redemption Policy',
      html: `
        <p><strong>Conversion Benchmark:</strong> 10 CBK Coins = ₹1.00 INR.</p>
        <p><strong>Minimum Threshold:</strong> Users can redeem starting at a threshold of 2,500 CBK Coins (₹250 INR) directly to any UPI VPA or IMPS account.</p>
        <p><strong>Settlement Speed:</strong> UPI payouts are disbursed instantly upon authorization.</p>
      `
    },
    cookies: {
      title: 'Cookie Settings & Affiliate Tracking',
      html: `
        <p>We use essential cookies and redirect telemetry tokens to accurately route and attribute cashback earnings from partner merchants to your personal account.</p>
        <p>You can manage session cookie preferences at any time in your browser settings.</p>
      `
    }
  };

  const openModal = (type) => {
    if (!legalModal || !modalContents[type]) return;
    modalTitle.textContent = modalContents[type].title;
    modalBody.innerHTML = modalContents[type].html;
    legalModal.classList.add('open');
    legalModal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';
  };

  const closeModal = () => {
    if (!legalModal) return;
    legalModal.classList.remove('open');
    legalModal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
  };

  legalTriggers.forEach(trigger => {
    trigger.addEventListener('click', (e) => {
      e.preventDefault();
      const modalType = trigger.getAttribute('data-modal');
      openModal(modalType);
    });
  });

  if (modalClose) modalClose.addEventListener('click', closeModal);
  if (modalDismiss) modalDismiss.addEventListener('click', closeModal);
  if (legalModal) {
    legalModal.addEventListener('click', (e) => {
      if (e.target === legalModal) closeModal();
    });
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && legalModal && legalModal.classList.contains('open')) {
      closeModal();
    }
  });

  // 9. Auto-Update Current Year
  const yearSpan = document.getElementById('currentYear');
  if (yearSpan) {
    yearSpan.textContent = new Date().getFullYear();
  }
});
