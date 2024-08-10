import os
import json
from pprint import pprint
import renderer
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from xpdf_process import figures_captions_list
import subprocess
import time

def run_pdf2htmlEX(input_file, output_dir):
    script_path = './run_pdf2htmlEX.sh'
    subprocess.check_call([script_path, input_file, output_dir])

if __name__ == "__main__":
    input_path = '/Users/duncanarbour/Library/CloudStorage/OneDrive-SyneosHealth/PDFigCapInput'
    output_path = '/Users/duncanarbour/Library/CloudStorage/OneDrive-SyneosHealth/PDFigCapInput/Output'
    xpdf_path = os.path.join(output_path, 'xpdf')
    log_file = os.path.join(output_path, 'log.text')
    f_log = open(log_file, 'w')

    if not os.path.isdir(xpdf_path):
        os.mkdir(xpdf_path)

    # Choose a DPI value for rendering
    customize_dpi = 300  # Example DPI value for high quality

    # Read each file in the input path
    for pdf in os.listdir(input_path):
        if pdf.endswith('.pdf') and (not pdf.startswith('._')):
            data = {}
            pdf_path = os.path.join(input_path, pdf)
            print(pdf_path)
            try:
                images = renderer.render_pdf(pdf_path, customize_dpi)
            except Exception as e:
                print(f"\nError rendering {pdf}: {e}\n")
                f_log.write(f"Error rendering {pdf}: {e}\n")
                continue

            data[pdf] = {}
            data[pdf]['figures'] = []
            data[pdf]['pages_annotated'] = []
            pdf_flag = 0
            pdf_output_path = os.path.join(xpdf_path, pdf[:-4])
            try:
                if not os.path.isdir(pdf_output_path):
                    os.mkdir(pdf_output_path)
                run_pdf2htmlEX(pdf_path, pdf_output_path)
            except Exception as e:
                print(f"\nError processing {pdf} with pdf2htmlEX: {e}\n")
                f_log.write(f"Error processing {pdf} with pdf2htmlEX: {e}\n")
                pdf_flag = 1

            if pdf_flag == 0:
                flag = 0
                wrong_count = 0
                while flag == 0 and wrong_count < 5:
                    try:
                        figures, info = figures_captions_list(input_path, pdf, xpdf_path)
                        flag = 1
                    except Exception as e:
                        wrong_count += 1
                        time.sleep(5)
                        print(f"Error processing {pdf}: {e}")
                        f_log.write(f"Error processing {pdf}: {e}\n")
                        info = {'fig_no_est': 0}
                        figures = []
                        print("------\nChrome Error\n----------\n")

                data[pdf]['fig_no'] = info['fig_no_est']

                output_file_path = os.path.join(output_path, pdf[:-4])
                if not os.path.isdir(output_file_path):
                    os.mkdir(output_file_path)

                for figure in figures:
                    page_no = int(figure[:-4][4:])
                    page_fig = images[page_no - 1]
                    rendered_size = page_fig.size

                    bboxes = figures[figure]
                    order_no = 0
                    for bbox in bboxes:
                        order_no += 1
                        png_ratio = float(rendered_size[1]) / info['page_height']
                        print(png_ratio)

                        if len(bbox[1]) > 0:
                            data[pdf]['figures'].append({
                                'page': page_no,
                                'region_bb': bbox[0],
                                'figure_type': 'Figure',
                                'page_width': info['page_width'],
                                'page_height': info['page_height'],
                                'caption_bb': bbox[1][0],
                                'caption_text': bbox[1][1]
                            })
                            with open(output_file_path + '/' + str(page_no) + '_' + str(order_no) + '.txt', 'w') as capoutput:
                                capoutput.write(str(bbox[1][1]))
                                capoutput.close()
                        else:
                            data[pdf]['figures'].append({
                                'page': page_no,
                                'region_bb': bbox[0],
                                'figure_type': 'Figure',
                                'page_width': info['page_width'],
                                'page_height': info['page_height'],
                                'caption_bb': [],
                                'caption_text': []
                            })
                        fig_extracted = page_fig.crop([int(bbox[0][0] * png_ratio), int(bbox[0][1] * png_ratio), 
                                                       int((bbox[0][0] + bbox[0][2]) * png_ratio), int((bbox[0][1] + bbox[0][3]) * png_ratio)])
                        fig_extracted.save(output_file_path + '/' + str(page_no) + '_' + str(order_no) + '.jpg')

                pprint(data)
                json_file = os.path.join(output_file_path, pdf[:-4] + '.json')
                with open(json_file, 'w') as outfile:
                    json.dump(data, outfile)
    f_log.close()



