async function copyImageToClipboard(dataUrl) {
    try {
        const response = await fetch(dataUrl);
        const blob = await response.blob();
        const item = new ClipboardItem({ "image/png": blob });
        await navigator.clipboard.write([item]);

    } catch (err) {
        alert('Impossible de copier l\'image dans le presse-papiers. Le navigateur pourrait avoir bloqué l\'accès ou une erreur est survenue.');
    }
}

async function genChartImage(chart_id) {
    const canvas = document.getElementById(chart_id);

    if (!canvas) {
        return;
    }

    const canvasImage = await html2canvas(canvas, {
        scale: 2,
        useCORS: true
    });

    return canvasImage
}

async function generatePdfFromChart(chart_id, mesure_name) {
    const canvasImage = await genChartImage(chart_id);
    const imgData = canvasImage.toDataURL('image/png');

    const { jsPDF } = window.jspdf;
    const pdf = new jsPDF('p', 'mm', 'a4');

    const pdfWidth = pdf.internal.pageSize.getWidth();
    const pdfHeight = pdf.internal.pageSize.getHeight();
    const margin = 15; 

    // --- Logo de l'entreprise ---
    const logoUrl = '/static/abmgood.png';
    const logoWidth = 40;
    const logoHeight = 20;
    const logoX = margin;
    const logoY = margin - 5;

    try {
        const response = await fetch(logoUrl);
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        const blob = await response.blob();
        const reader = new FileReader();
        reader.readAsDataURL(blob);
        
        await new Promise(resolve => {
            reader.onloadend = function() {
                const base64data = reader.result;
                pdf.addImage(base64data, 'PNG', logoX, logoY, logoWidth, logoHeight);
                resolve();
            }
        });
    } catch (error) {
        console.error("Erreur lors de l'ajout du logo :", error);
    }

    // --- En-tête du PDF ---
    pdf.setFontSize(22);
    pdf.setTextColor(44, 62, 80);
    pdf.text("Rapport de mesure", pdfWidth / 2, margin + 10, { align: 'center' });
    
    pdf.setFontSize(10);
    pdf.setTextColor(127, 140, 141);
    pdf.text(`Généré le: ${new Date().toLocaleDateString('fr-FR')}`, pdfWidth - margin, margin + 18, { align: 'right' });

    // --- Ajout du titre de la mesure ---
    let yPos = margin + 35;
    pdf.setFontSize(16);
    pdf.setTextColor(52, 73, 94);
    const measureTitleWrapped = pdf.splitTextToSize(`Mesure: ${mesure_name}`, pdfWidth - (2 * margin));
    pdf.text(measureTitleWrapped, margin, yPos);
    yPos += (measureTitleWrapped.length * 7) + 10;

    // --- Ajout de l'image du graphique ---
    const imgAspectRatio = canvasImage.width / canvasImage.height;
    const imgWidthPdf = pdfWidth - (2 * margin);
    let imgHeightPdf = imgWidthPdf / imgAspectRatio;

    // Si l'image est trop grande pour une page, ajustez
    if (yPos + imgHeightPdf > pdfHeight - margin) {
        
        if (imgHeightPdf > pdfHeight - margin - yPos) {
             imgHeightPdf = pdfHeight - margin - yPos;
             imgWidthPdf = imgHeightPdf * imgAspectRatio;
        }
        if (imgHeightPdf < 50) {
            pdf.addPage();
            yPos = margin;
            imgWidthPdf = pdfWidth - (2 * margin);
            imgHeightPdf = imgWidthPdf / imgAspectRatio;
        }
    }
    
    pdf.addImage(imgData, 'PNG', margin, yPos, imgWidthPdf, imgHeightPdf);
    yPos += imgHeightPdf + 15; 

    // --- Champ de saisie interactif (AcroForm) ---
    const fieldWidth = pdfWidth - (2 * margin);
    const fieldHeight = 80;

    if (yPos + fieldHeight + 20 > pdfHeight - margin) {
        pdf.addPage();
        yPos = margin;
    }

    pdf.setFontSize(14);
    pdf.setTextColor(52, 73, 94);
    pdf.text("Notes :", margin, yPos);
    yPos += 10;
    var notesField = new window.jspdf.AcroForm.TextField()
    notesField.Rect = [margin, yPos, fieldWidth, fieldHeight]
    notesField.multiline = true;
    notesField.value = ""
    pdf.addField(notesField);
    yPos += fieldHeight + 15;


    // --- Pied de page simple ---
    pdf.setFontSize(8);
    pdf.setTextColor(127, 140, 141);
    pdf.text("© 2025 ABM x GalTechDev. All Rights Reserved.", pdfWidth / 2, pdfHeight - 10, { align: 'center' });

    return pdf
}

document.addEventListener("DOMContentLoaded", function () {
    const mesure = decodeURIComponent(document.location.pathname.replace("/mesure/", ""))

    types_data.forEach(type_data => {
        let print_button = document.getElementById("print-button-"+type_data)
        print_button.classList.remove("cursor-not-allowed")

        print_button.addEventListener("click", (event) => {
            generatePdfFromChart("graph-"+type_data, mesure).then((pdf) => {
                const pdfBlob = pdf.output('blob');
                const blobUrl = URL.createObjectURL(pdfBlob);
                console.log(blobUrl)
                const iframe = document.createElement('iframe');
                iframe.style.display = 'none';

                iframe.src = blobUrl

                iframe.onload = function() {
                    iframe.contentWindow.print()
                    const onFocus = () => {
                        window.removeEventListener("focus", onFocus)
                        document.body.removeChild(iframe);
                        iframe.remove()
                        URL.revokeObjectURL(blobUrl);
                    }
                    window.addEventListener("focus", onFocus)
                }

                document.body.appendChild(iframe);
               
            })
        });

        let save_button = document.getElementById("save-button-"+type_data)
        save_button.classList.remove("cursor-not-allowed")

        save_button.addEventListener("click", (event) => {
            generatePdfFromChart("graph-"+type_data, mesure).then((pdf) => {
                pdf.save(`ABM repport ${mesure_name}.pdf`)
            })
        });

        let copy_button = document.getElementById("copy-button-"+type_data)
        copy_button.classList.remove("cursor-not-allowed")

        copy_button.addEventListener("click", (event) => {
            genChartImage("graph-"+type_data).then((canvasImage) => {
                const imgData = canvasImage.toDataURL('image/png');
                copyImageToClipboard(imgData)
            })
        });
    })
})