const mp = new MercadoPago('APP_USR-fcf50003-8f80-407b-8e02-8056bce15fd7');
const bricksBuilder = mp.bricks();

mp.bricks().create("wallet", "wallet_container", {
    initialization: {
        preferenceId: "{{ preference_id }}",
    },
    callbacks: {
        onReady: () => {},
        onSubmit: () => {},
        onError: (error) => console.error(error),
    },
    customization: {
        texts: {
            valueProp: 'smart_option',
        },
    },
});

