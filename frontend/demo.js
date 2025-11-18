/**
 * OrderHub Demo/Tutorial System
 * Handles welcome modal, interactive tutorial, and onboarding flow
 */

// Tutorial steps configuration
const TUTORIAL_STEPS = [
  {
    id: 'client-view',
    target: '[data-tutorial-step="client-view"]',
    title: 'Client View - What Your Customers See',
    content: 'This is what your clients see on their phone - a regular WhatsApp or Email interface. <strong>Important:</strong> This demo shows a visual representation, but in reality, orders come from your clients\' own phones through their WhatsApp or Email. This is just a preview of what they see.',
    position: 'bottom',
    action: function(context) {
      context.viewMode = 'client';
      context.activeTab = 'submit';
      context.interfaceMode = 'whatsapp';
    }
  },
  {
    id: 'restaurant-name',
    target: '[data-tutorial-step="restaurant-name-input"]',
    title: 'Enter Restaurant Name',
    content: 'First, enter the restaurant name in this field. This identifies which restaurant the order is from.',
    position: 'bottom',
    action: function(context) {
      context.activeTab = 'submit';
      context.viewMode = 'client';
      const input = document.querySelector('[data-tutorial-step="restaurant-name-input"]');
      if (input) {
        context.$nextTick(() => input.focus());
      }
    }
  },
  {
    id: 'message-input',
    target: '[data-tutorial-step="message-input"]',
    title: 'Type Your Order',
    content: 'Type the order message here, just like your clients would send it via WhatsApp. For example: "2 kg tomatoes, 5 pieces chicken, 1 liter milk".',
    position: 'top',
    action: function(context) {
      context.activeTab = 'submit';
      const input = document.querySelector('[data-tutorial-step="message-input"]');
      if (input) {
        context.$nextTick(() => input.focus());
      }
    }
  },
  {
    id: 'send-button',
    target: '[data-tutorial-step="send-button"]',
    title: 'Submit the Order',
    content: 'Click this button to submit the order. The system will parse the order and extract products, quantities, and units automatically.',
    position: 'top',
    action: function(context) {
      context.activeTab = 'submit';
    }
  },
  {
    id: 'feed-tab',
    target: '[data-tutorial-step="tab-feed"]',
    title: 'Check Live Feed',
    content: 'After submitting an order, click on the <strong>Live Feed</strong> tab to see your order appear in real-time. This shows all orders from today.',
    position: 'bottom',
    action: function(context) {
      context.navigate('/feed');
    }
  },
  {
    id: 'feed-section',
    target: '[data-tutorial-step="feed-section"]',
    title: 'Review and Edit Orders',
    content: 'In the Live Feed, you can:<br>• View all orders from today<br>• Click on an order to see details<br>• Edit products, quantities, or units if needed<br>• Check the order when it\'s ready to process<br><br>Orders can be edited and marked as checked when ready.',
    position: 'top',
    action: function(context) {
      context.activeTab = 'feed';
      context.loadFeed();
    }
  },
  {
    id: 'history-tab',
    target: '[data-tutorial-step="tab-history"]',
    title: 'View Order History',
    content: 'Click on the <strong>History</strong> tab to see all orders stored over time. This is where all your orders are saved for future reference.',
    position: 'bottom',
    action: function(context) {
      context.navigate('/history');
    }
  },
  {
    id: 'history-section',
    target: '[data-tutorial-step="history-section"]',
    title: 'Order History',
    content: 'The History page stores all orders throughout time. You can browse past orders, view details, and track order history by restaurant and date.',
    position: 'top',
    action: function(context) {
      context.activeTab = 'history';
      context.loadHistory();
    }
  },
  {
    id: 'messages-link',
    target: '[data-tutorial-step="messages-link"]',
    title: 'Messages Page',
    content: 'Click on <strong>Messages</strong> to see all messages sent from clients. Messages that aren\'t orders (like questions or conversations) are stored here.',
    position: 'bottom',
    action: function(context) {
      // Just highlight, don't navigate yet
    }
  },
  {
    id: 'user-view-button',
    target: '[data-tutorial-step="user-view-button"]',
    title: 'User View - Reply to Clients',
    content: 'Switch to <strong>User View</strong> to see how you can reply to clients. When you reply from this software, the message is sent from your own phone to the client\'s phone. This demonstrates the two-way communication flow.',
    position: 'left',
    action: function(context) {
      context.viewMode = 'user';
      context.activeTab = 'submit';
    }
  }
];

/**
 * Demo/Tutorial mixin for Alpine.js components
 * Use this to add tutorial functionality to your component
 */
function createDemoMixin() {
  return {
    // Tutorial state
    showWelcomeModal: false,
    tutorialActive: false,
    tutorialStep: 0,
    tutorialSteps: [],
    currentTutorialStep: null,
    tutorialTargetElement: null,
    tutorialPositionKey: 0, // Force recalculation on resize

    initTutorial() {
      // Check if welcome modal should be shown
      const welcomeSeen = localStorage.getItem('orderhub_welcome_seen') === 'true';
      const tutorialCompleted = localStorage.getItem('orderhub_tutorial_completed') === 'true';
      
      if (!welcomeSeen) {
        this.showWelcomeModal = true;
      } else if (!tutorialCompleted) {
        // Auto-start tutorial if welcome was seen but tutorial not completed
        this.$nextTick(() => {
          this.startTutorial();
        });
      }
      
      // Initialize tutorial steps (bind actions to this context)
      this.tutorialSteps = TUTORIAL_STEPS.map(step => ({
        ...step,
        action: step.action ? () => step.action(this) : null
      }));
    },

    startTutorial() {
      // Ensure tutorial steps are initialized
      if (this.tutorialSteps.length === 0) {
        this.initTutorial();
      }
      this.tutorialActive = true;
      this.tutorialStep = 0;
      this.showWelcomeModal = false;
      localStorage.setItem('orderhub_welcome_seen', 'true');
      // Don't mark as completed when restarting
      localStorage.removeItem('orderhub_tutorial_completed');
      this.updateTutorialStep();
    },

    startTutorialFromWelcome() {
      this.showWelcomeModal = false;
      localStorage.setItem('orderhub_welcome_seen', 'true');
      this.$nextTick(() => {
        this.startTutorial();
      });
    },

    skipWelcome() {
      this.showWelcomeModal = false;
      localStorage.setItem('orderhub_welcome_seen', 'true');
    },

    skipTutorial() {
      this.tutorialActive = false;
      this.tutorialStep = 0;
      localStorage.setItem('orderhub_tutorial_completed', 'true');
      this.currentTutorialStep = null;
      this.tutorialTargetElement = null;
    },

    nextTutorialStep() {
      if (this.tutorialStep < this.tutorialSteps.length - 1) {
        this.tutorialStep++;
        this.updateTutorialStep();
      } else {
        // Tutorial completed
        this.tutorialActive = false;
        localStorage.setItem('orderhub_tutorial_completed', 'true');
        this.currentTutorialStep = null;
        this.tutorialTargetElement = null;
      }
    },

    previousTutorialStep() {
      if (this.tutorialStep > 0) {
        this.tutorialStep--;
        this.updateTutorialStep();
      }
    },

    updateTutorialStep() {
      // Ensure tutorial steps are initialized
      if (this.tutorialSteps.length === 0) {
        this.initTutorial();
      }
      
      if (this.tutorialStep >= 0 && this.tutorialStep < this.tutorialSteps.length) {
        const step = this.tutorialSteps[this.tutorialStep];
        // Set current step immediately so tooltip shows
        this.currentTutorialStep = step;
        this.tutorialTargetElement = null; // Reset target element
        
        // Execute step action if provided
        if (step && step.action) {
          step.action();
        }
        
        // Wait for DOM update, then find and highlight target element
        // Use multiple $nextTick calls to ensure DOM is fully updated after tab switches
        this.$nextTick(() => {
          this.$nextTick(() => {
            // Try to find the target element with a small delay to ensure it's rendered
            setTimeout(() => {
              if (step && step.target) {
                const target = document.querySelector(step.target);
                this.tutorialTargetElement = target;
                
                if (target) {
                  // Scroll element into view
                  target.scrollIntoView({ behavior: 'smooth', block: 'center' });
                } else {
                  console.warn('Tutorial target not found:', step.target, 'Step:', step.id);
                }
              }
            }, 200);
          });
        });
      } else {
        console.error('Invalid tutorial step:', this.tutorialStep, 'Total steps:', this.tutorialSteps.length);
        this.currentTutorialStep = null;
      }
    },

    getTutorialTooltipStyle() {
      // Access tutorialPositionKey to make this reactive to window resize
      const _ = this.tutorialPositionKey;
      
      // If no current step, center the tooltip
      if (!this.currentTutorialStep) {
        return 'top: 50%; left: 50%; transform: translate(-50%, -50%);';
      }
      
      // If no target element yet, center the tooltip
      if (!this.tutorialTargetElement) {
        return 'top: 50%; left: 50%; transform: translate(-50%, -50%);';
      }
      
      const rect = this.tutorialTargetElement.getBoundingClientRect();
      const position = this.currentTutorialStep.position || 'bottom';
      const tooltipWidth = 384; // max-w-sm = 384px
      const tooltipHeight = 200; // approximate height
      const viewportWidth = window.innerWidth;
      const viewportHeight = window.innerHeight;
      
      // For the first step (client-view), position tooltip to the LEFT of the phone
      if (this.currentTutorialStep.id === 'client-view') {
        // Find the actual phone element (iPhone Frame) instead of the container
        const phoneElement = document.querySelector('[data-tutorial-phone="true"]');
        
        // Use phone element if found, otherwise fall back to container
        const phoneRect = phoneElement ? phoneElement.getBoundingClientRect() : rect;
        
        const spacing = 30; // Spacing between phone and tooltip (not touching)
        const minMargin = 20; // Minimum margin from screen edges
        
        // Calculate phone position
        const phoneLeft = phoneRect.left;
        const phoneCenterY = phoneRect.top + (phoneRect.height / 2);
        
        // Always position to the LEFT of the phone with fixed spacing
        // Calculate position: phone left edge - tooltip width - spacing
        let left = phoneLeft - tooltipWidth - spacing;
        let top = phoneCenterY;
        
        // CRITICAL: Ensure tooltip never overlaps or goes behind the phone
        // The right edge of tooltip must be at least 'spacing' pixels away from phone's left edge
        const tooltipRightEdge = left + tooltipWidth;
        if (tooltipRightEdge >= phoneLeft - spacing) {
          // If too close or overlapping, push it further left
          left = phoneLeft - tooltipWidth - spacing;
        }
        
        // If tooltip would go off screen on the left, we need to handle it carefully
        // But still maintain spacing from phone - don't let it go behind
        if (left < minMargin) {
          // Check if we can fit it without going behind phone
          const maxLeft = phoneLeft - tooltipWidth - spacing;
          if (maxLeft >= minMargin) {
            // We can fit it properly
            left = maxLeft;
          } else {
            // Screen is too small - position at minimum margin but ensure it doesn't overlap
            left = minMargin;
            // Double-check it's not behind phone
            if (left + tooltipWidth > phoneLeft - spacing) {
              // Screen too small - position as far left as possible while maintaining spacing
              left = Math.max(minMargin, phoneLeft - tooltipWidth - spacing);
            }
          }
        }
        
        // Ensure tooltip stays within viewport vertically
        const tooltipTop = top - (tooltipHeight / 2);
        const tooltipBottom = top + (tooltipHeight / 2);
        
        if (tooltipTop < minMargin) {
          top = minMargin + (tooltipHeight / 2);
        } else if (tooltipBottom > viewportHeight - minMargin) {
          top = viewportHeight - minMargin - (tooltipHeight / 2);
        }
        
        return `top: ${top}px; left: ${left}px; transform: translateY(-50%);`;
      }
      
      // For large elements (like client-view container), center the tooltip on screen
      // Check if element takes up more than 40% of viewport width or height
      const isLargeElement = (rect.width > viewportWidth * 0.4) || (rect.height > viewportHeight * 0.4);
      
      // For other large elements, center on screen
      if (isLargeElement) {
        // Center on screen but slightly above center for better visibility
        return `top: 40%; left: 50%; transform: translate(-50%, -50%);`;
      }
      
      const offset = 20;
      let top = 0;
      let left = 0;
      let transform = '';
      
      switch (position) {
        case 'top':
          top = rect.top - offset;
          left = rect.left + (rect.width / 2);
          transform = 'translate(-50%, -100%)';
          break;
        case 'bottom':
          top = rect.bottom + offset;
          left = rect.left + (rect.width / 2);
          transform = 'translate(-50%, 0)';
          break;
        case 'left':
          top = rect.top + (rect.height / 2);
          left = rect.left - offset;
          transform = 'translate(-100%, -50%)';
          break;
        case 'right':
          top = rect.top + (rect.height / 2);
          left = rect.right + offset;
          transform = 'translate(0, -50%)';
          break;
        default:
          top = rect.bottom + offset;
          left = rect.left + (rect.width / 2);
          transform = 'translate(-50%, 0)';
      }
      
      // Ensure tooltip stays within viewport
      if (left < tooltipWidth / 2) {
        left = tooltipWidth / 2 + 10;
      } else if (left > viewportWidth - tooltipWidth / 2) {
        left = viewportWidth - tooltipWidth / 2 - 10;
      }
      
      if (top < 10) {
        top = 10;
      } else if (top + tooltipHeight > viewportHeight - 10) {
        top = viewportHeight - tooltipHeight - 10;
      }
      
      return `top: ${top}px; left: ${left}px; transform: ${transform};`;
    },

    getTutorialHighlightStyle() {
      if (!this.tutorialTargetElement) {
        return 'display: none;';
      }
      
      const rect = this.tutorialTargetElement.getBoundingClientRect();
      const padding = 8; // Add some padding around the element
      
      return `
        top: ${rect.top - padding}px;
        left: ${rect.left - padding}px;
        width: ${rect.width + (padding * 2)}px;
        height: ${rect.height + (padding * 2)}px;
      `;
    }
  };
}

// Export for use in other files
if (typeof window !== 'undefined') {
  window.DemoMixin = createDemoMixin;
  window.TUTORIAL_STEPS = TUTORIAL_STEPS;
}

