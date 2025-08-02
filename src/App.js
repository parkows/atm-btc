import React, { useState } from 'react';
import { 
  Box, 
  Card, 
  CardContent, 
  Typography, 
  Button, 
  Grid, 
  Container,
  AppBar,
  Toolbar,
  IconButton
} from '@mui/material';
import {
  CreditCard as CreditCardIcon,
  QrCode as QrCodeIcon,
  Phone as PhoneIcon,
  AccountBalance as AccountBalanceIcon,
  AttachMoney as MoneyIcon,
  CurrencyBitcoin as BitcoinIcon
} from '@mui/icons-material';
import BitcoinModal from './BitcoinModal';
import './App.css';

function App() {
  const [selectedCard, setSelectedCard] = useState(null);
  const [bitcoinModalOpen, setBitcoinModalOpen] = useState(false);

  const handleCardClick = (cardId) => {
    setSelectedCard(cardId);
    if (cardId === 'bitcoin') {
      setBitcoinModalOpen(true);
    }
  };

  const handleCloseBitcoinModal = () => {
    setBitcoinModalOpen(false);
    setSelectedCard(null);
  };

  const cards = [
    {
      id: 'card',
      title: 'OPERACIONES CON TARJETA',
      icon: <CreditCardIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      logos: ['VISA', 'mastercard'],
      color: '#ffffff'
    },
    {
      id: 'qr',
      title: 'RETIRÁ CON QR',
      icon: <QrCodeIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      color: '#ffffff'
    },
    {
      id: 'recharge',
      title: 'RECARGÁ',
      icon: <PhoneIcon sx={{ fontSize: 40, color: '#1976d2' }} />,
      logos: ['SUBE', 'Movistar', 'personal', 'personal Pay', 'Claro'],
      color: '#ffffff'
    },
    {
      id: 'bitcoin',
      title: 'VENDER BITCOIN',
      icon: <BitcoinIcon sx={{ fontSize: 40, color: '#f7931a' }} />,
      subtitle: 'Lightning Network',
      color: '#ffffff',
      highlight: true
    },
    {
      id: 'deposits',
      title: 'DEPÓSITOS',
      icon: <MoneyIcon sx={{ fontSize: 40, color: '#ffffff' }} />,
      color: '#666666',
      disabled: true
    }
  ];

  return (
    <Box sx={{ 
      minHeight: '100vh', 
      background: 'linear-gradient(135deg, #1e3c72 0%, #2a5298 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      {/* Header */}
      <AppBar position="static" sx={{ backgroundColor: 'transparent', boxShadow: 'none' }}>
        <Toolbar>
          <Typography variant="h6" sx={{ color: 'white', flexGrow: 1 }}>
            VE
          </Typography>
        </Toolbar>
      </AppBar>

      {/* Main Content */}
      <Container maxWidth="md" sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column', py: 4 }}>
        {/* Title */}
        <Typography 
          variant="h4" 
          sx={{ 
            color: 'white', 
            textAlign: 'center', 
            mb: 4, 
            fontWeight: 'bold',
            textShadow: '2px 2px 4px rgba(0,0,0,0.3)'
          }}
        >
          Selecione sua operação
        </Typography>

        {/* Cards Grid */}
        <Grid container spacing={3} sx={{ flexGrow: 1 }}>
          {cards.map((card) => (
            <Grid item xs={12} sm={6} md={4} key={card.id}>
              <Card 
                sx={{ 
                  height: 200,
                  backgroundColor: card.color,
                  cursor: card.disabled ? 'default' : 'pointer',
                  transition: 'all 0.3s ease',
                  transform: selectedCard === card.id ? 'scale(1.05)' : 'scale(1)',
                  boxShadow: selectedCard === card.id ? '0 8px 25px rgba(0,0,0,0.3)' : '0 4px 15px rgba(0,0,0,0.2)',
                  border: card.highlight ? '3px solid #f7931a' : 'none',
                  '&:hover': {
                    transform: card.disabled ? 'scale(1)' : 'scale(1.05)',
                    boxShadow: card.disabled ? '0 4px 15px rgba(0,0,0,0.2)' : '0 8px 25px rgba(0,0,0,0.3)'
                  }
                }}
                onClick={() => !card.disabled && handleCardClick(card.id)}
              >
                <CardContent sx={{ 
                  height: '100%', 
                  display: 'flex', 
                  flexDirection: 'column', 
                  justifyContent: 'center',
                  alignItems: 'center',
                  textAlign: 'center'
                }}>
                  {card.icon}
                  <Typography 
                    variant="h6" 
                    sx={{ 
                      mt: 2, 
                      fontWeight: 'bold',
                      color: card.disabled ? '#999' : '#1976d2'
                    }}
                  >
                    {card.title}
                  </Typography>
                  {card.subtitle && (
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: '#f7931a',
                        fontWeight: 'bold',
                        mt: 1
                      }}
                    >
                      {card.subtitle}
                    </Typography>
                  )}
                  {card.logos && (
                    <Box sx={{ mt: 2, display: 'flex', gap: 1, flexWrap: 'wrap', justifyContent: 'center' }}>
                      {card.logos.map((logo, index) => (
                        <Typography 
                          key={index} 
                          variant="caption" 
                          sx={{ 
                            backgroundColor: '#f5f5f5',
                            padding: '2px 8px',
                            borderRadius: '4px',
                            fontSize: '0.7rem',
                            fontWeight: 'bold'
                          }}
                        >
                          {logo}
                        </Typography>
                      ))}
                    </Box>
                  )}
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* Footer */}
      <Box sx={{ 
        backgroundColor: 'rgba(0,0,0,0.1)', 
        py: 2, 
        px: 3,
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center'
      }}>
        {/* RedATM Logo */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Box sx={{ 
            width: 30, 
            height: 30, 
            backgroundColor: 'white', 
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            color: '#1976d2'
          }}>
            A
          </Box>
          <Box>
            <Typography variant="h6" sx={{ color: 'white', fontWeight: 'bold' }}>
              RedATM
            </Typography>
            <Typography variant="caption" sx={{ color: 'white', opacity: 0.8 }}>
              Mucho más que un cajero.
            </Typography>
          </Box>
        </Box>

        {/* CONVENIOS Button */}
        <Button 
          variant="outlined" 
          sx={{ 
            borderColor: 'white', 
            color: 'white',
            '&:hover': {
              borderColor: 'white',
              backgroundColor: 'rgba(255,255,255,0.1)'
            }
          }}
        >
          CONVENIOS
        </Button>
      </Box>

      {/* Bitcoin Modal */}
      <BitcoinModal 
        open={bitcoinModalOpen} 
        onClose={handleCloseBitcoinModal} 
      />
    </Box>
  );
}

export default App; 