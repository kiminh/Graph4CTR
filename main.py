# -*- coding:utf-8 -*-
# @Time: 2020/1/14 9:08
# @Author: jockwang, jockmail@126.com
import torch
from data import MyDataset
from graph import getGraph
from model import Model, train
from processtor import process
from torch.utils.data import DataLoader
from utils import seed_everything
import logging
import argparse

LOG_FORMAT = "%(asctime)s %(levelname)s: %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT, datefmt=DATE_FORMAT)


def main(args):
    if args is None:
        logging.info('Args lossing...')
        return
    dataset = args.dataset
    mode = args.mode
    hidden_size = args.hidden
    batch_size = args.batch
    if args.gpu:
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    else:
        device = torch.device('cpu')
    logging.info('Use '+str(device)+'.')
    logging.info('data processing...')
    user, item, all_ = process(dataset=dataset, bathpath=args.path+'data/')
    number = {
        'u': user,
        'i': item,
        'a': all_,
    }
    logging.info('loading train, test set...')
    data = {
        'train': DataLoader(MyDataset(mode='train', item_size=number['a'], dataset=dataset),
                            batch_size=batch_size, shuffle=True),
        'test': DataLoader(MyDataset(mode='test', item_size=number['a'], dataset=dataset),
                           batch_size=batch_size, shuffle=False),
    }
    graph = getGraph(number, dataset)
    logging.info('initialization model...')
    i_hidden_list = [16, 4]
    hidden_list = [1,]
    model = Model(u_hidden_size=hidden_size, i_hidden_size=hidden_size, number=number,
                  i_hidden_list=i_hidden_list, hidden_list=hidden_list, args=args, heads=6,
                  dataset=dataset, mode=mode)
    metrics = ['auc', 'f1', 'acc', 'precision', 'recall']
    logging.info('============================Training===============================')
    train(model=model, data=data, metrics=metrics, graph=graph, device=device, epochs=args.epoch,
          learning_rate=args.learning_rate, weight_decay=args.weight_decay, path=args.path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--dataset', type=str, default='book', help='choose a dataset: book, movie, or others.')
    parser.add_argument('--mode', type=str, default='GAT', help='choose an algorithm of GNN: GCN, GAT, or other.')
    parser.add_argument('--epoch', type=int, default=30, help='the epoch size.')
    parser.add_argument('--batch', type=int, default=64, help='the batch size.')
    parser.add_argument('--hidden', type=int, default=4, help='the embedding size of user and item.')
    parser.add_argument('--learning_rate', type=float, default=0.001, help='Learning rate.')
    parser.add_argument('--weight_decay', type=float, default=0., help='L2 regularization.')
    parser.add_argument('--gpu', type=bool, default=True, help='use gpu.')
    parser.add_argument('--c_in', type=float, default=1., help='C_in.')
    parser.add_argument('--c_out', type=float, default=1., help='C_out.')
    parser.add_argument('--path', type=str, default='/content/drive/My Drive/Colab Notebooks/Graph4CTR/', help='Path.')
    parser.print_help()

    args = parser.parse_args()
    seed_everything()
    main(args)
