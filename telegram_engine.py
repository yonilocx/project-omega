<div style="text-align: center; margin: 20px 0;">
    <h2 style="color: #f0b90b; font-family: sans-serif;">AI Live ICT Analysis (FVG & Levels)</h2>
    <div style="background: #131722; padding: 15px; border-radius: 10px; display: inline-block; border: 1px solid #333;">
        <img id="liveAichart" src="ict_setup.png" alt="AI ICT Setup Analysis" style="max-width: 100%; width: 900px; border-radius: 6px;">
    </div>
</div>

<script>
  // Auto-refresh the image every 10 seconds to display new AI setups
  setInterval(() => {
    const img = document.getElementById('liveAichart');
    if (img) {
      img.src = 'ict_setup.png?timestamp=' + new Date().getTime();
    }
  }, 10000);
</script>